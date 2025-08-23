from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CsvSchema:
    columns = (
        "test_id",
        "title",
        "risk",
        "manual_time_min",
        "candidate_for_automation",
        "dev_time_hours",
        "exec_time_sec",
        "maintenance_pct_per_month",
        "runs_per_release_override",
    )

    tester_columns = (
        "name",
        "role",
        "monthly_salary",
        "hours_per_month"
    )

class ExampleData:
    @staticmethod
    def data_frame() -> pd.DataFrame:
        dataframe = pd.DataFrame({
            "test_id": ["TC-001", "TC-002", "TC-003"],
            "title": [
                "Login - valid creds",
                "Password reset flow",
                "Profile update",
            ],
            "risk": ["High", "Medium", "Low"],
            "manual_time_min": [5, 4, 7],
            "candidate_for_automation": ["Yes", "Yes", "No"],
            "dev_time_hours": [2.0, 1.5, 3.0],
            "exec_time_sec": [8, 10, 12],
            "maintenance_pct_per_month": [5, 4, 6],
            "runs_per_release_override": ["", "", 2],
        })

        return dataframe[list(CsvSchema.columns)]


class ExampleTesters:
    @staticmethod
    def tester_data_frame() -> pd.DataFrame:
        tester_df = pd.DataFrame({
            "name": ["Tester 1", "Tester 2", "Tester 3", "Tester 4"],
            "role": ["manual", "manual", "automation", "automation"],
            "monthly_salary": [20000, 25000, 40000, 32000],
            "hours_per_month": [160, 160, 160, 160],
        })

        return tester_df[list(CsvSchema.tester_columns)]
