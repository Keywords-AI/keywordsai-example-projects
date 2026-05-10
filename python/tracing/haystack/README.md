# Haystack Respan Tracing Examples

These examples cover Respan's Haystack instrumentation package:

```bash
cd /home/yuyang/KeywordsAI/respan-example-projects/python/tracing/haystack
pip install -r requirements.txt
cp .env.example .env
```

For local package development, install from source instead:

```bash
pip install -e /home/yuyang/KeywordsAI/respan/python-sdks/respan \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-sdk \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-tracing \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-haystack \
            haystack-ai python-dotenv jq markdown-it-py mdit_plain trafilatura
```

Run any numbered unit script directly:

```bash
python 00_setup_tracing.py
python 02_pipeline_run.py
```

Gateway scripts route OpenAI-compatible Haystack calls through Respan and require `RESPAN_API_KEY`.
The prompt-management gateway script also requires `RESPAN_PROMPT_ID` for a deployed Respan prompt.
Set `RESPAN_PROMPT_VARIABLES_JSON` when the managed prompt uses custom variable names.

Run the complex edge case separately:

```bash
python complex_edge_cases.py
```

## Scripts

| Script | Coverage |
| --- | --- |
| `00_setup_tracing.py` | Respan tracing setup with an offline Haystack pipeline |
| `01_setup_respan_gateway.py` | Respan gateway setup for `OpenAIGenerator` |
| `complex_edge_cases.py` | Complex single-trace pipeline with preprocessing, routing, retrieval, joining, prompt building, generation, answer building, adapting, and handled failure cases |
| `02_pipeline_run.py` | `Pipeline.run` |
| `03_async_pipeline_run.py` | `AsyncPipeline.run_async` |
| `04_prompt_builder.py` | `PromptBuilder` |
| `05_chat_prompt_builder.py` | `ChatPromptBuilder` |
| `06_answer_builder.py` | `AnswerBuilder` |
| `07_output_adapter.py` | `OutputAdapter` |
| `08_document_writer.py` | `DocumentWriter` |
| `09_cache_checker.py` | `CacheChecker` |
| `10_in_memory_bm25_retriever.py` | `InMemoryBM25Retriever` |
| `11_in_memory_embedding_retriever.py` | `InMemoryEmbeddingRetriever` |
| `12_document_cleaner.py` | `DocumentCleaner` |
| `13_text_cleaner.py` | `TextCleaner` |
| `14_document_splitter.py` | `DocumentSplitter` |
| `15_recursive_document_splitter.py` | `RecursiveDocumentSplitter` |
| `16_markdown_header_splitter.py` | `MarkdownHeaderSplitter` |
| `17_document_joiner.py` | `DocumentJoiner` |
| `18_answer_joiner.py` | `AnswerJoiner` |
| `19_branch_joiner.py` | `BranchJoiner` |
| `20_list_joiner.py` | `ListJoiner` |
| `21_string_joiner.py` | `StringJoiner` |
| `22_conditional_router.py` | `ConditionalRouter` |
| `23_document_length_router.py` | `DocumentLengthRouter` |
| `24_document_type_router.py` | `DocumentTypeRouter` |
| `25_file_type_router.py` | `FileTypeRouter` |
| `26_metadata_router.py` | `MetadataRouter` |
| `27_top_p_sampler.py` | `TopPSampler` |
| `28_json_schema_validator.py` | `JsonSchemaValidator` |
| `29_regex_text_extractor.py` | `RegexTextExtractor` |
| `30_answer_exact_match_evaluator.py` | `AnswerExactMatchEvaluator` |
| `31_document_recall_evaluator.py` | `DocumentRecallEvaluator` |
| `32_document_mrr_evaluator.py` | `DocumentMRREvaluator` |
| `33_document_map_evaluator.py` | `DocumentMAPEvaluator` |
| `34_document_ndcg_evaluator.py` | `DocumentNDCGEvaluator` |
| `35_csv_to_document.py` | `CSVToDocument` |
| `36_json_converter.py` | `JSONConverter` |
| `37_markdown_to_document.py` | `MarkdownToDocument` |
| `38_text_file_to_document.py` | `TextFileToDocument` |
| `39_html_to_document.py` | `HTMLToDocument` |
| `40_tool_invoker.py` | `ToolInvoker` |
| `41_openai_generator_gateway.py` | `OpenAIGenerator` through Respan gateway |
| `42_openai_chat_generator_gateway.py` | `OpenAIChatGenerator` through Respan gateway |
| `43_prompt_management_gateway.py` | Respan prompt management through Haystack `OpenAIChatGenerator` and the Respan gateway |
