Load Type Rules

FULL load refreshes the complete dataset.
APPEND load inserts only new records and does not update old records.
INCREMENTAL load processes only new or changed records using a watermark column.
UPSERT load inserts new records and updates existing records using primary keys.
UPSERT should not be used without primary keys.
INCREMENTAL should not be used without a watermark column.