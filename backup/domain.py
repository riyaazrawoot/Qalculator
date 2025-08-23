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

class ExampleData:
    @staticmethod
    def dataframe() -> pd.DataFrame:
        df = pd.DataFrame({
            "test_id": ["TC-001","TC-002","TC-003"],
            "title": [
                "Login - valid creds",
                "Password reset flow",
                "Profile update",
            ],
            "risk": ["High","Medium","Low"],
            "manual_time_min": [5,4,7],
            "candidate_for_automation": ["Yes","Yes","No"],
            "dev_time_hours": [2.0,1.5,3.0],
            "exec_time_sec": [8,10,12],
            "maintenance_pct_per_month": [5,4,6],
            "runs_per_release_override": ["","",2],
        })
        # Ensure column order
        return df[list(CsvSchema.columns)]
