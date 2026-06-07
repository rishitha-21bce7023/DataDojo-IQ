Troubleshooting Guide

Issue: UPSERT failed
Possible cause: Missing primary keys or duplicate keys in source data.

Issue: Incremental load missed records
Possible cause: Incorrect watermark column or wrong comparison condition.

Issue: Schema mismatch
Possible cause: Source has new columns that are not mapped in metadata.

Issue: Trigger did not run
Possible cause: Trigger disabled incorrect schedule or wrong environment setting.

Issue: Merge conflict
Possible cause: Multiple source rows matched the same target row.