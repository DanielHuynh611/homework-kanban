-- Apply once to an existing production database before restarting the app.
-- The constraint prevents two accounts from being created for one email.
-- First inspect the result below: it must return zero rows.
SELECT email, COUNT(*) AS duplicate_count
FROM f_8e00a8e9__users
GROUP BY email
HAVING COUNT(*) > 1;

SET @email_index_exists = (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'f_8e00a8e9__users'
    AND index_name = 'uq_f_8e00a8e9_users_email'
);
SET @email_index_sql = IF(
  @email_index_exists = 0,
  'ALTER TABLE f_8e00a8e9__users ADD UNIQUE KEY uq_f_8e00a8e9_users_email (email)',
  'SELECT ''Email uniqueness index already exists'' AS migration_status'
);
PREPARE email_index_statement FROM @email_index_sql;
EXECUTE email_index_statement;
DEALLOCATE PREPARE email_index_statement;
