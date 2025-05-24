import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class BenchmarkProgress:
    current_progress: int
    total_prompts: int
    is_complete: bool


@dataclass
class BenchmarkResult:
    request_lens: list[int]
    request_ids: list[str]
    total_tokens: list[int]
    prompt_lens: list[int]
    response_lens: list[int]
    e2e_latencies: list[float]
    per_token_latencies: list[float]
    inference_latencies: list[float]
    waiting_latencies: list[float]
    decode_token_latencies: list[float]


class BenchmarkLogParser:
    def __init__(self):
        self.progress_pattern = re.compile(r"num_finised_requests: (\d+)")
        self.total_prompts_pattern = re.compile(r"num_prompts=(\d+)")
        self.array_pattern = re.compile(r"all_(\w+)=\[(.*?)\]")

    def parse_progress(self, log_text: str) -> Optional[BenchmarkProgress]:
        """Parse the progress from benchmark log text.

        Args:
            log_text: The benchmark log text

        Returns:
            BenchmarkProgress if progress information is found, None otherwise
        """
        # Find total prompts
        total_match = self.total_prompts_pattern.search(log_text)
        if not total_match:
            return None
        total_prompts = int(total_match.group(1))

        # Find current progress
        progress_matches = self.progress_pattern.findall(log_text)
        if not progress_matches:
            return None

        current_progress = int(progress_matches[-1])
        is_complete = current_progress >= total_prompts

        return BenchmarkProgress(
            current_progress=current_progress,
            total_prompts=total_prompts,
            is_complete=is_complete,
        )

    def parse_result(self, log_text: str) -> Optional[BenchmarkResult]:
        """Parse the benchmark results from log text.

        Args:
            log_text: The benchmark log text

        Returns:
            BenchmarkResult if all required arrays are found, None otherwise
        """
        # Required array names
        required_arrays = [
            "request_lens",
            "request_ids",
            "total_tokens",
            "prompt_lens",
            "response_lens",
            "e2e_latencies",
            "per_token_latencies",
            "inference_latencies",
            "waiting_latencies",
            "decode_token_latencies",
        ]

        # Parse all arrays
        arrays = {}
        for match in self.array_pattern.finditer(log_text):
            name = match.group(1)
            values_str = match.group(2)

            # Parse values based on type
            if name == "request_ids":
                values = [v.strip("'") for v in values_str.split(", ")]
            else:
                values = [
                    float(v) if "." in v else int(v) for v in values_str.split(", ")
                ]

            arrays[name] = values

        # Check if all required arrays are present
        if not all(name in arrays for name in required_arrays):
            return None

        return BenchmarkResult(
            request_lens=arrays["request_lens"],
            request_ids=arrays["request_ids"],
            total_tokens=arrays["total_tokens"],
            prompt_lens=arrays["prompt_lens"],
            response_lens=arrays["response_lens"],
            e2e_latencies=arrays["e2e_latencies"],
            per_token_latencies=arrays["per_token_latencies"],
            inference_latencies=arrays["inference_latencies"],
            waiting_latencies=arrays["waiting_latencies"],
            decode_token_latencies=arrays["decode_token_latencies"],
        )


global_benchmark_parser = BenchmarkLogParser()
