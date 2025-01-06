# vtt-convert

將 Whisper 轉換出的 vtt 資料進行：

* 台灣中文化
* 修正標點和空格問題
* 根據領域知識修正辨識錯字

您可能會需要修改 `main.py` 來符合您的需求。

## Whisper command

我是基於這個命令來進行語音辨識的。

```bash
mlx_whisper --language Chinese --model mlx-community/whisper-large-v3-mlx audio.wav --condition-on-previous-text False -f vtt
```
