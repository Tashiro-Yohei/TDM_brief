import streamlit as st
import google.generativeai as genai
import markdown
from weasyprint import HTML
import io

# ページ設定（ワイドレイアウト）
st.set_page_config(page_title="Talk Design Brief Generator", layout="wide")

def generate_brief(api_key, product_info, gap_info):
    """Gemini APIを呼び出してブリーフを生成する"""
    genai.configure(api_key=api_key)
    # 適切なモデルを選択（gemini-1.5-proを推奨）
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    あなたは優秀なマーケターです。
    以下の「商品情報」と「トークギャップ診断結果」をもとに、トークデザインマーケティングの実行要件定義書（ブリーフ）を作成してください。

    【入力情報】
    ・商品情報（名前またはURL）: {product_info}
    ・トークギャップ診断結果: {gap_info}

    【出力要件】
    以下の構成に従い、Markdown形式で出力してください。
    出力する内容は、上記の入力情報を分析し、具体的なマーケティング戦略として昇華させたものにしてください。

    # トークデザイン・プロジェクト 実行要件定義書

    ## 1. プロジェクト背景と目的
    （市場・ブランドの現状、コミュニケーションのゴール）

    ## 2. ターゲット・インサイト
    （コアターゲット、ターゲットの「会話」の現状）

    ## 3. トークギャップ診断結果（前提課題）
    （自社の発信内容、SNSでの発信内容、生成AIの言及内容、ギャップの核心を整理）

    ## 4. コア戦略：トークデザイン要件
    （トーク・フック、トーク・コンテキスト、トーク・アセット、トーク・サーキュレーションの4要素の具体案）

    ## 5. 実行戦術のプランニング要件
    （全体戦術方針、コミュニケーション戦術、メディア・チャネル戦術、話題の増幅・連鎖の仕組み。※生成AIへの言及を促す視点を必ず入れること）

    ---
    ## 【別AIインプット用】WHO / WHAT / HOW 整理
    このプロジェクトを別のAIに引き継ぐための要件整理として、以下の項目を具体的に記述してください。
    * **WHO**：ペルソナ設計／インサイト抽出／カスタマージャーニー分析
    * **WHAT**：ポジショニング／POD（Point of Difference）／プロポジション設計
    * **HOW**：IMCテーマ策定／施策立案／KPI設計／予算配分の考え方
    """
    
    response = model.generate_content(prompt)
    return response.text

def create_pdf(markdown_text):
    """MarkdownをHTML経由でPDFに変換する"""
    # MarkdownをHTMLに変換
    html_body = markdown.markdown(markdown_text, extensions=['tables'])
    
    # PDF用のCSSとHTMLの骨組み
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
            }}
            body {{
                font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', sans-serif;
                color: #333;
                line-height: 1.6;
                font-size: 10.5pt;
            }}
            h1 {{ font-size: 18pt; color: #1A365D; border-bottom: 2px solid #1A365D; padding-bottom: 5px; }}
            h2 {{ font-size: 14pt; color: #1A365D; border-left: 5px solid #1A365D; padding-left: 10px; margin-top: 30px; }}
            h3 {{ font-size: 12pt; color: #2B6CB0; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f0f4f8; }}
            hr {{ border: none; border-top: 2px dashed #ccc; margin: 30px 0; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # WeasyPrintでPDFを生成し、メモリ上のバイナリデータとして返す
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# UIレイアウト設計
st.title("🗣️ トークデザイン・ブリーフ自動生成アプリ")

# 画面を左カラム（インプット）と右カラム（アウトプット）に分割
col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("Input (要件入力)")
    st.markdown("必要な情報を入力し、生成ボタンを押してください。")
    
    api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studioで取得したAPIキーを入力してください。")
    
    product_info = st.text_input("商品名 または 商品URL", placeholder="例：〇〇ビール、https://...")
    
    gap_info = st.text_area(
        "トークギャップ診断結果", 
        height=200, 
        placeholder="自社の発信したい内容と、SNSや生成AIでの言及内容のギャップを入力してください。"
    )
    
    generate_btn = st.button("ブリーフを生成する", type="primary", use_container_width=True)

with col_right:
    st.header("Output (ブリーフ確認・出力)")
    
    # セッションステートの初期化
    if 'brief_content' not in st.session_state:
        st.session_state.brief_content = ""
        
    if generate_btn:
        if not api_key:
            st.error("API Keyを入力してください。")
        elif not product_info or not gap_info:
            st.error("商品情報とトークギャップ診断結果を入力してください。")
        else:
            with st.spinner("Geminiがブリーフを作成中...（数十秒かかる場合があります）"):
                try:
                    result = generate_brief(api_key, product_info, gap_info)
                    st.session_state.brief_content = result
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    # 生成されたコンテンツがある場合、画面に表示＆PDFダウンロードボタンを配置
    if st.session_state.brief_content:
        st.markdown(st.session_state.brief_content)
        
        st.divider()
        
        # PDF生成
        with st.spinner("PDFを作成準備中..."):
            pdf_file = create_pdf(st.session_state.brief_content)
            
        st.download_button(
            label="📄 確定してPDFを出力する",
            data=pdf_file,
            file_name="talk_design_brief.pdf",
            mime="application/pdf",
            type="primary"
        )