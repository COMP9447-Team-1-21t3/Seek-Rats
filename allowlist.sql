CREATE OR REPLACE FUNCTION generate_repo (repo_id text) RETURNS bool
  AS $$
  BEGIN
    /* TO DO */
  END;
  $$ LANGUAGE plpgsql
  
CREATE OR REPLACE FUNCTION rebase_repo (repo_id_old text, repo_id_new text) RETURNS bool
  AS $$
  BEGIN
    /* TO DO */
  END;
  $$ LANGUAGE plpgsql
  
CREATE OR REPLACE FUNCTION copy_whitelist (repo_id_old text, repo_id_new text) RETURNS bool
  AS $$
  BEGIN
    /* TO DO */
  END;
  $$ LANGUAGE plpgsql
  
 CREATE OR REPLACE FUNCTION clear_whitelist (repo_id text) RETURNS bool
  AS $$
  BEGIN
    /* TO DO */
  END;
  $$ LANGUAGE plpgsql
