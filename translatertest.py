from googletrans import Translator

def main():
    # Translatorオブジェクトを作成
    translator = Translator()
    translator.raise_exception = True  # Add this line

    # 翻訳したいテキスト
    text_to_translate = "Hello, how are you?"

    # テキストを翻訳
    translated = translator.translate(text_to_translate, dest='ja')

    # 翻訳結果を表示
    print(f"Original: {text_to_translate}")
    print(f"Translated: {translated.text}")

if __name__ == "__main__":
    main()
