# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：`glossary_search_glossary`（用語集サーバー。宿題で `glossary_get_lecture_summary` を追加後は 2 個）
- STEP 2 の [tool call]：`glossary_search_glossary({'query': '3レベル'})`
- STEP 3 の [tool call]：`fetch_fetch({'url': 'https://modelcontextprotocol.io/'})`
- STEP 4 の [tool call]：`aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview'})`
- 気づき・疑問：
  - 設定ファイルに数行足すだけで、外部のツールがエージェントから使えた。その一方で、ツールの名前と説明文は、サーバーの作者が決める。
  - fetch サーバーのツールの説明文には、「このツールでインターネットにアクセスできるようになった」という趣旨の英語の文が入っていた。説明文はそのままモデルに渡るので、足す前に提供元と説明文を確認する必要があると感じた。
  - STEP 4 の AWS サーバーには、起動するコマンドがなく、質問の内容が AWS に送られる。外部のサーバーを足すときは、送られる情報も把握する必要がある。

## 宿題

- 取り組んだレベル：基礎
- やったこと：
  - `app/mcp_server.py` の TODO の 1 行を、`server.tool()(tools.get_lecture_summary)` に置き換えて、要点を返すツールを公開した。書き換えたのはサーバー側だけで、エージェント側（`app/mcp_agent.py`）は変えていない。
- 結果：
  - `--list-tools` で、`glossary_get_lecture_summary` が一覧に増えたことを確認した（ツールは 7 個から 8 個に増えた）。
  - 「第3回では何を学ぶ？」と質問すると、`glossary_get_lecture_summary({'lecture': 3})` が呼ばれ、第3回の要点（「AIエージェント」）を基に答えた（入力 5,862 トークン、出力 248 トークン、モデル応答 2 回）。
- 気づき・疑問：
  - 公開するツールを 1 つ足すだけで、エージェントがそのツールを選んで使うようになった。説明文（docstring）が、モデルがツールを選ぶ手がかりになっている。
  - 疑問：ツールが増えると、モデルが適切なツールを選べなくなることはあるか。
