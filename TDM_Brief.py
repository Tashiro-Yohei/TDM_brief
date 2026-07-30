import streamlit as st
import google.generativeai as genai
import markdown
from weasyprint import HTML
import io

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

    /* ボタンのモダン化（グラデーション、シャドウ、ホバーエフェクト） */
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

    /* インプットエリアのフォーカス時のGlowエフェクト */
    .stTextInput input {
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #26D0CE;
        box-shadow: 0 0 0 2px rgba(38, 208, 206, 0.2);
    }

    /* Streamlitのデフォルト要素を非表示にしてアプリ感を強める */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 左カラムの背景を少し変えてパネル風にする（任意） */
    [data-testid="column"]:nth-of-type(1) {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02);
    }
</style>
""", unsafe_allow_html=True)
# ==========================================

def generate_brief(api_key, product_name, product_url, gap_info):
    """Gemini APIを呼び出してブリーフを生成する"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    あなたは優秀なマーケターです。
    以下の「商品情報」と「トークギャップ診断結果」をもとに、トークデザインマーケティングの実行要件定義書（ブリーフ）を作成してください。

    【入力情報】
    ・商品名: {product_name}
    ・商品URL: {product_url if product_url else '（指定なし）'}
    ・トークギャップ診断結果ファイルの内容:
    {gap_info}

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
    html_body = markdown.markdown(markdown_text, extensions=['tables'])
    
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
    
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# ==========================================
# 🖥️ UIレイアウト設計
# ==========================================
st.title("TALK DESIGN BRIEF GENERATOR")
st.markdown("##### AI駆動型 トークデザイン要件定義書 自動生成システム")

# 左カラム(インプット) 1 : 右カラム(アウトプット) 3 の比率
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
        type=["txt", "csv", "md"],
        help="UTF-8エンコードのテキスト、CSV、Markdown形式のファイル"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 ブリーフを生成する", type="primary", use_container_width=True)

with col_right:
    st.markdown("### 📄 Output (ブリーフプレビュー)")
    
    # セッションステートの初期化
    if 'brief_content' not in st.session_state:
        st.session_state.brief_content = ""
        st.info("👈 左側のパネルに要件を入力し、「ブリーフを生成する」ボタンを押してください。")
        
    if generate_btn:
        gap_info = None
        if uploaded_file is not None:
            try:
                gap_info = uploaded_file.getvalue().decode("utf-8")
            except Exception as e:
                st.error("ファイルの読み込みに失敗しました。UTF-8形式で保存されたファイルを使用してください。")
                
        if not api_key:
            st.warning("API Keyを入力してください。")
        elif not product_name:
            st.warning("商品名を入力してください。")
        elif uploaded_file is None:
            st.warning("トークギャップ診断結果のファイルをアップロードしてください。")
        elif gap_info is None:
            st.error("ファイルの内容を正しく取得できませんでした。")
        else:
            with st.spinner("🧠 Geminiがブリーフを策定中... (数十秒かかる場合があります)"):
                try:
                    result = generate_brief(api_key, product_name, product_url, gap_info)
                    st.session_state.brief_content = result
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    # 生成されたコンテンツがある場合
    if st.session_state.brief_content:
        # プレビュー表示
        with st.container():
            st.markdown(st.session_state.brief_content)
        
        st.divider()
        
        # PDF生成＆ダウンロード
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
