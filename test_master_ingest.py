import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.master_ingest import get_versioned_project_name

def test_get_versioned_project_name():
    existing = ["ProjectA", "Wedding_v1", "Wedding_v2"]
    assert get_versioned_project_name("ProjectA", existing) == "ProjectA_v2"
    assert get_versioned_project_name("Wedding", existing) == "Wedding_v3"
    assert get_versioned_project_name("NewProject", existing) == "NewProject"

if __name__ == "__main__":
    test_get_versioned_project_name()
    print("ALL TESTS PASSED")
