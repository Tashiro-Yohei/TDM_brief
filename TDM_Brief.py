import streamlit as st
import google.generativeai as genai
import markdown
from weasyprint import HTML
import io
import tempfile
import os

# ページ設定（ワイドレイアウトとタイトル）
st.set_page_config(page_title="Talk Design Brief Generator", layout="wide")

# ==========================================
# 🎨 カスタムCSS（スタイリッシュ＆モダンデザイン）
# ==========================================
st.markdown("""
<style>
    /* 全体のフォント設定 */
    .stApp {
        font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', sans-serif;
    }
    
    /* 大見出し（H1）のグラデーションテキスト */
    h1 {
        background: -webkit-linear-gradient(45deg, #1A2980, #26D0CE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: 1px;
        padding-bottom: 10px;
    }
    
    /* 中見出し（H2）のクリーンな装飾 */
    h2 {
        color: #1A365D;
        font-weight: 700;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 10px;
        margin-top: 20px;
    }

    /* ボタンのモダン化 */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1A2980 0%, #26D0CE 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 700;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(38, 208, 206, 0.3);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(38, 208, 206, 0.5);
        border: none;
        color: white;
    }

    /* インプットエリア */
    .stTextInput input {
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #26D0CE;
        box-shadow: 0 0 0 2px rgba(38, 208, 206, 0.2);
    }

    /* Streamlit要素非表示 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 左カラムパネル風 */
    [data-testid="column"]:nth-of-type(1) {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02);
    }
</style>
""", unsafe_allow_html=True)
# ==========================================

def generate_brief(api_key, product_name, product_url, uploaded_file):
    """Gemini APIのマルチモーダル機能を利用してファイルを直接解析する"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        uploaded_gemini_file = genai.upload_file(path=tmp_file_path)

        prompt = f"""
        あなたは優秀なマーケターです。
        添付した「トークギャップ診断結果ファイル（画像・テキスト含む）」と、以下の「商品情報」をもとに、トークデザインマーケティングの実行要件定義書（ブリーフ）を作成してください。

        【商品情報】
        ・商品名: {product_name}
        ・商品URL: {product_url if product_url else '（指定なし）'}

        【出力要件】
        以下の構成に従い、Markdown形式で出力してください。
        添付ファイルから画像内の文字情報や傾向も読み取り、具体的なマーケティング戦略として昇華させてください。
        読者が理解しやすいよう、適宜「箇条書き」や「太字（**文字**）」を活用してメリハリをつけてください。

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
        
        response = model.generate_content([prompt, uploaded_gemini_file])
        result_text = response.text
        
        genai.delete_file(uploaded_gemini_file.name)
        return result_text

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

def create_pdf(markdown_text):
    """MarkdownをHTML経由でPDFに変換する（スタイリッシュデザイン版）"""
    html_body = markdown.markdown(markdown_text, extensions=['tables'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            /* Google Fontsから日本語フォントを読み込む */
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
            
            @page {{
                size: A4;
                margin: 25mm 20mm;
                /* 右下にページ番号を追加 */
                @bottom-right {{
                    content: counter(page);
                    font-family: 'Noto Sans JP', sans-serif;
                    font-size: 9pt;
                    color: #64748b;
                }}
            }}
            
            body {{
                font-family: 'Noto Sans JP', sans-serif;
                color: #334155; /* 視認性の高いダークグレー */
                line-height: 1.8; /* 行間を広げて読みやすく */
                font-size: 10.5pt;
                word-wrap: break-word;
            }}
            
            /* 大見出し：ドキュメントタイトル */
            h1 {{ 
                font-size: 20pt; 
                color: #1A365D; 
                text-align: center;
                border-bottom: 3px solid #26D0CE; 
                padding-bottom: 12px; 
                margin-bottom: 35px;
                font-weight: 700; 
            }}
            
            /* 中見出し：セクションの区切り */
            h2 {{ 
                font-size: 14pt; 
                color: #1A365D; 
                background-color: #F8FAFC;
                border-left: 6px solid #1A2980; 
                padding: 10px 15px; 
                margin-top: 40px; 
                margin-bottom: 20px;
                font-weight: 700;
                page-break-after: avoid; /* 見出しの直後で改ページさせない */
            }}
            
            /* 小見出し */
            h3 {{ 
                font-size: 12pt; 
                color: #2B6CB0; 
                border-bottom: 1px dashed #CBD5E1;
                padding-bottom: 6px;
                margin-top: 25px;
                margin-bottom: 15px;
                font-weight: 700; 
                page-break-after: avoid;
            }}
            
            p {{
                margin-bottom: 15px;
                text-align: justify;
            }}
            
            /* リスト（箇条書き）のデザイン調整 */
            ul, ol {{
                margin-top: 5px;
                margin-bottom: 20px;
                padding-left: 25px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            
            /* 強調文字をネイビーにして目立たせる */
            strong {{
                color: #1A2980;
                font-weight: 700;
            }}
            
            /* テーブルのデザイン */
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin-top: 15px;
                margin-bottom: 25px;
                page-break-inside: avoid;
            }}
            th, td {{ 
                border: 1px solid #E2E8F0; 
                padding: 12px; 
                text-align: left; 
            }}
            th {{ 
                background-color: #1A365D; 
                color: white;
                font-weight: 500;
            }}
            tr:nth-child(even) {{
                background-color: #F8FAFC;
            }}
            
            /* 区切り線 */
            hr {{ 
                border: none; 
                border-top: 2px solid #E2E8F0; 
                margin: 40px 0; 
            }}
            
            /* 引用・注釈ブロック */
            blockquote {{
                border-left: 4px solid #26D0CE;
                background-color: #F0FDFA;
                margin: 15px 0;
                padding: 12px 15px;
                color: #0F766E;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# ==========================================
# 🖥️ UIレイアウト設計
# ==========================================
st.title("TALK DESIGN BRIEF GENERATOR")
st.markdown("##### AI駆動型 トークデザイン要件定義書 自動生成システム")

col_left, col_right = st.columns([1, 3])

with col_left:
    st.markdown("### 📝 Input (要件入力)")
    
    api_key = st.text_input("🔑 Gemini API Key", type="password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    product_name = st.text_input("🏷️ 商品名", placeholder="例：〇〇ビール")
    product_url = st.text_input("🔗 商品URL（任意）", placeholder="https://...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📊 トークギャップ診断結果 (Upload)", 
        type=["pdf", "csv", "txt", "png", "jpg", "jpeg", "md"],
        help="【推奨】PowerPoint資料は、スライド内の画像やグラフの文字も含めてAIに正確に読み取らせるため、必ず「PDFファイル」として保存（エクスポート）してからアップロードしてください。"
    )
    
    st.info("💡 **PowerPointをご利用の方へ**\n\nパワポ(.pptx)のままではなく、**「PDFとして保存」**したファイルをアップロードしていただくことで、スライド内の図解やテキストをAIが残さず読み取れるようになります。")
    
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 ブリーフを生成する", type="primary", use_container_width=True)

with col_right:
    st.markdown("### 📄 Output (ブリーフプレビュー)")
    
    if 'brief_content' not in st.session_state:
        st.session_state.brief_content = ""
        st.info("👈 左側のパネルに要件を入力し、「ブリーフを生成する」ボタンを押してください。")
        
    if generate_btn:
        if not api_key:
            st.warning("API Keyを入力してください。")
        elif not product_name:
            st.warning("商品名を入力してください。")
        elif uploaded_file is None:
            st.warning("トークギャップ診断結果のファイルをアップロードしてください。")
        else:
            with st.spinner("🧠 Gemini 2.5 Flashがファイルを直接「視覚・言語」で解析し、ブリーフを策定中... (最大1分ほどかかります)"):
                try:
                    result = generate_brief(api_key, product_name, product_url, uploaded_file)
                    st.session_state.brief_content = result
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}\n\n※APIキーが間違っていないか、または非対応のファイル形式でないかご確認ください。")

    if st.session_state.brief_content:
        with st.container():
            st.markdown(st.session_state.brief_content)
        
        st.divider()
        
        with st.spinner("📄 PDFをレンダリング中..."):
            pdf_file = create_pdf(st.session_state.brief_content)
            
        st.download_button(
            label="📥 確定してPDFをダウンロード",
            data=pdf_file,
            file_name="talk_design_brief.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
