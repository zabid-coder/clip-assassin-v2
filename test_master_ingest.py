import unittest
from modules.master_ingest import get_versioned_project_name

class TestMasterIngest(unittest.TestCase):
    def test_versioned_project_name(self):
        existing = ["Project_A", "Project_B_v2"]
        self.assertEqual(get_versioned_project_name("Project_C", existing), "Project_C")
        self.assertEqual(get_versioned_project_name("Project_A", existing), "Project_A_v2")
        
        existing_v2 = ["Project_A", "Project_A_v2"]
        self.assertEqual(get_versioned_project_name("Project_A", existing_v2), "Project_A_v3")

if __name__ == "__main__":
    unittest.main()
    print("ALL TESTS PASSED")
