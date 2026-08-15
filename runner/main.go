// runner drives the dbt pipeline (deps, seed, snapshot, build) with
// per-step retries, so a transient BigQuery/network error doesn't fail
// the whole Cloud Run Job.
package main

import (
	"fmt"
	"os"
	"os/exec"
	"time"
)

const maxAttempts = 3

var steps = []struct {
	name string
	args []string
}{
	{"deps", []string{"deps"}},
	{"seed", []string{"seed", "--vars", "{load_source_data: true}"}},
	{"snapshot", []string{"snapshot"}},
	{"build", []string{"build"}},
}

func runStep(name string, args []string) error {
	var lastErr error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		fmt.Printf("==> %s (attempt %d/%d): dbt %v\n", name, attempt, maxAttempts, args)
		cmd := exec.Command("dbt", args...)
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

func main() {
	for _, s := range steps {
		if err := runStep(s.name, s.args); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	fmt.Println("All dbt steps completed successfully")
}
