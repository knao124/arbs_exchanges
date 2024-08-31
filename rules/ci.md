## CI の要件

### 共通

- 各アプリケーションごとに workflow を作成する

### Python の CI

- 以下を実行する
  - pytest
- pytest の詳細
  - pytest を使用して、プロジェクト配下の tests/以下のファイルを実行する
  - 実行結果（成功・失敗）を Slack に通知する
