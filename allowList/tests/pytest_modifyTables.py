import allowlist_modifyTables
from tests_helpers import gen_random_strings

org_id = "123456"

@pytest.fixture
def test_create_table(db_resource):
    allowlist_modifyTables.create_organization_table(org_id, db_resource)
    yield

def integration_test():
    

    """
    Functions to test:
        allowlist_modifyTables.create_organization_table()
        allowlist_modifyTables.read_repo()
        allowlist_modifyTables.read_repo_with_info()
        allowlist_modifyTables.insert_new_term()
        allowlist_modifyTables.insert_new_terms()
        allowlist_modifyTables.insert_new_terms_with_info()
        allowlist_modifyTables.delete_term()
        allowlist_modifyTables.delete_repo()
        allowlist_modifyTables.delete_table()
    """
    allowlist_modifyTables.create_organization_table()
