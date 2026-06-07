Pipeline Configuration Rules

1. Every pipeline configuration must include project name source system source table target table business domain and environment.
2. Raw and bronze layers are mandatory.
3. Silver layer is required for curated business ready data.
4. Gold layer is optional and should be used for reporting ready outputs.
5. UPSERT requires primary key columns.
6. INCREMENTAL requires a watermark column.
7. Every generated configuration must be valid JSON.