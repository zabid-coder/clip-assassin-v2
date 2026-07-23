import unittest
from modules.master_ingest import get_versioned_project_name

class TestMasterIngest(unittest.TestCase):
    def test_versioned_project_name(self):
        existing = ["Project_A", "Project_B_v2"]
        self.assertEqual(get_versioned_project_name("Project_C", existing), "Project_C")
        self.assertEqual(get_versioned_project_name("Project_A", existing), "Project_A_v2")
        
        existing_v2 = ["Project_A", "Project_A_v2"]
        self.assertEqual(get_versioned_project_name("Project_A", existing_v2), "Project_A_v3")

    def test_create_master_folder_structure(self):
        import tempfile, shutil, os
        from modules.master_ingest import create_master_folder_structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            success, msg, path = create_master_folder_structure(tmpdir, "Test Project", "Client X", "Standard Video", "2026-07-25")
            self.assertTrue(success)
            self.assertTrue(os.path.exists(path))
            self.assertIn("2026-07-25_Client X_Test Project", path)
            self.assertTrue(os.path.exists(os.path.join(path, "Raw Footages", "Card 01")))
            self.assertTrue(os.path.exists(os.path.join(path, "Davinci Resolve Database")))
            self.assertTrue(os.path.exists(os.path.join(path, "Logos & Branding")))
            self.assertTrue(os.path.exists(os.path.join(path, "Exports")))

if __name__ == "__main__":
    unittest.main()
    print("ALL TESTS PASSED")
