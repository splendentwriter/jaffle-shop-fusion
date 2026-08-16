// runner drives the dbt pipeline (deps, snapshot, build, test) with
// per-step retries, so a transient BigQuery/network error doesn't fail
// the whole Cloud Run Job. Reports the outcome to Slack.
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"time"
)

const (
	maxAttempts    = 3
	pipelineScript = "pipeline.sh"
)

var steps = []string{"deps", "snapshot", "build", "test"}

func runStep(name string) error {
	var lastErr error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		fmt.Printf("==> %s (attempt %d/%d): %s %s\n", name, attempt, maxAttempts, pipelineScript, name)
		cmd := exec.Command("sh", pipelineScript, name)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		lastErr = cmd.Run()
		if lastErr == nil {
			return nil
		}
		fmt.Printf("==> %s failed (attempt %d/%d): %v\n", name, attempt, maxAttempts, lastErr)
		if attempt < maxAttempts {
			backoff := time.Duration(attempt) * 5 * time.Second
			fmt.Printf("==> retrying %s in %s\n", name, backoff)
			time.Sleep(backoff)
		}
	}
	return fmt.Errorf("%s failed after %d attempts: %w", name, maxAttempts, lastErr)
}

func notifySlack(text string) {
	webhookURL := os.Getenv("SLACK_WEBHOOK_URL")
	if webhookURL == "" {
		fmt.Println("==> SLACK_WEBHOOK_URL not set, skipping Slack notification")
		return
	}
	payload, err := json.Marshal(map[string]string{"text": text})
	if err != nil {
		fmt.Fprintf(os.Stderr, "==> failed to build Slack payload: %v\n", err)
		return
	}
	resp, err := http.Post(webhookURL, "application/json", bytes.NewReader(payload))
	if err != nil {
		fmt.Fprintf(os.Stderr, "==> failed to send Slack notification: %v\n", err)
		return
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		fmt.Fprintf(os.Stderr, "==> Slack notification returned status %d\n", resp.StatusCode)
	}
}

func main() {
	for _, s := range steps {
		if err := runStep(s); err != nil {
			fmt.Fprintln(os.Stderr, err)
			notifySlack(fmt.Sprintf(":x: jaffle-shop-fusion dbt pipeline failed at step *%s*: %v", s, err))
			os.Exit(1)
		}
	}
	fmt.Println("All dbt steps completed successfully")
	notifySlack(":white_check_mark: jaffle-shop-fusion dbt pipeline completed successfully")
}
