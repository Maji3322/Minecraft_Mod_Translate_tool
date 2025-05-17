from deep_translator import GoogleTranslator

def main():
    # 翻訳したいテキスト
    text_to_translate = "Hello, how are you?"

    # GoogleTranslatorオブジェクトを使って英語から日本語に翻訳
    translated_text = GoogleTranslator(source='auto', target='ja').translate(text_to_translate)

    # 結果を表示
    print(f"Original: {text_to_translate}")
    print(f"Translated: {translated_text}")

if __name__ == "__main__":
    main()
