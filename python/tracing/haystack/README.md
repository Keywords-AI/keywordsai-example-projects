# Haystack Respan Tracing Examples

These examples cover Respan's Haystack instrumentation package:

```bash
cd python/tracing/haystack
pip install -r requirements.txt
```

The requirements file links the local Respan core, OpenInference bridge, and
Haystack instrumentation packages and constrains Haystack to the supported 2.x
line.

Run any numbered unit script directly:

```bash
python 00_setup_tracing.py
python 02_pipeline_run.py
python run_all.py
```

Set `RESPAN_EXAMPLE_RUN_ID` to attach one exact marker to every script in a
complete batch run.

Gateway scripts route OpenAI-compatible Haystack calls through Respan and require `RESPAN_API_KEY`.
They do not require `OPENAI_API_KEY`: the examples point Haystack's OpenAI-compatible components at the Respan gateway, and keys with credits can use Respan-managed model credentials.
`43_prompt_management_gateway.py` also requires `RESPAN_PROMPT_ID` for an existing deployed Respan prompt.
`44_prompt_management_extra_body_gateway.py` creates and deploys a managed prompt with `RESPAN_API_KEY`, then passes the returned `prompt_id` and variables through `generation_kwargs.extra_body.prompt`.
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
| `44_prompt_management_extra_body_gateway.py` | Creates and deploys a Respan managed prompt, then passes only `prompt_id` and variables through Haystack `generation_kwargs.extra_body` while the LLM call uses Respan gateway credits |
