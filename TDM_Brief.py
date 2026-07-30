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

    /* 左カラムパネル風 */
    [data-testid="column"]:nth-of-type(1) {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02);
    }
    
    /* =========================================
       📄 プレビュー画面（Markdown出力）のスタイリング
       ========================================= */
    [data-testid="stMarkdownContainer"] h1 {
        font-size: 1.8rem;
        color: #1A365D;
        border-bottom: 3px solid #26D0CE;
        padding-bottom: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    [data-testid="stMarkdownContainer"] h2 {
        font-size: 1.3rem;
        color: #1A365D;
        background-color: #F8FAFC;
        border-left: 6px solid #1A2980;
        padding: 0.8rem 1rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-radius: 0 4px 4px 0;
    }
    [data-testid="stMarkdownContainer"] h3 {
        font-size: 1.1rem;
        color: #2B6CB0;
        border-bottom: 1px dashed #CBD5E1;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    [data-testid="stMarkdownContainer"] strong {
        color: #1A2980;
        background: linear-gradient(transparent 70%, #E0F2FE 0%);
    }
    [data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] ol {
        margin-bottom: 1.5rem;
    }
    [data-testid="stMarkdownContainer"] li {
        margin-bottom: 0.5rem;
        line-height: 1.7;
        color: #334155;
    }
    [data-testid="stMarkdownContainer"] p {
        line-height: 1.7;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)
# ==========================================

def generate_brief(api_key, product_name, product_url, uploaded_file):
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
        添付した「トークギャップ診断結果ファイル（画像・テキスト含む）」と、以下の「商品情報」をもとに、トークデザインマーケティングの「実行要件定義書（オリエンテーション用ブリーフ）」を作成してください。

        【商品情報】
        ・商品名: {product_name}
        ・商品URL: {product_url if product_url else '（指定なし）'}

        【戦略の最重要方針（必ず遵守すること）】
        本プロジェクトの目的は「生活者やAIの既存の認識・インサイトにブランドを合わせる」ことではありません。
        「生活者やAIの認識を、ブランドが本来発信したい内容（理想の認識）へと近づけ、変容させる（パーセプションチェンジ）」ことが最大の目的です。
        したがって、各要件は「現状のインサイトに迎合する」のではなく、「誤認識をいかに解き、正しい認識（ブランドの意図）をいかに植え付けるか」という視点で策定してください。

        【重要な指示】
        この資料は「具体的なキャンペーン施策（クリエイティブ案や具体的なハッシュタグなど）」を提案するものではありません。
        代理店やクリエイターに対して「具体的なキャンペーンを企画・提案してもらうため」の【要件（ガイドライン、方向性、満たすべき条件）】を定義する資料です。具体的なアイデアを出しすぎず、企画の「枠組み」や「狙い」を提示してください。

        【出力要件】
        以下の構成に従い、Markdown形式で出力してください。
        読者が理解しやすいよう、適宜「箇条書き」や「太字（**文字**）」を活用してメリハリをつけてください。

        # トークデザイン・プロジェクト 実行要件定義書

        ## 1. プロジェクト背景と目的
        （市場・ブランドの現状、コミュニケーションのゴール。※「ブランドの意図する認識への変容」をゴールとして設定すること）

        ## 2. ターゲット・インサイト
        （コアターゲット、ターゲットの「会話」の現状。※現状のインサイトに迎合するのではなく、変容させるべき「現在の認識の壁」として捉えること）

        ## 3. トークギャップ診断結果（前提課題）
        （自社の発信内容、SNSでの発信内容、生成AIの言及内容、解決すべきギャップの核心を整理）

        ## 4. コア戦略：トークデザイン要件（企画の方向性）
        ※具体的な企画案ではなく、「どのような企画を提案してほしいか」という要件を定義してください。
        * **トーク・フックの要件**: ターゲットの既存の認識を揺さぶり、ブランドの本来のメッセージへ目を向けさせるための「きっかけ」の条件
        * **トーク・コンテキストの要件**: ターゲットやAIの認識を変容させるために、どのような世の中の文脈とブランドを接続すべきかの方向性
        * **トーク・アセットの要件**: 新しい認識を定着させ、会話を活性化させるために「どのような種類のコンテンツやツール」が必要かの指針
        * **トーク・サーキュレーションの要件**: 正しい認識（情報）が波及・循環していくための導線設計で満たすべき条件

        ## 5. 実行戦術のプランニング要件（施策立案のガイドライン）
        ※具体的な戦術ではなく、プランニングする上での指針を記載してください。
        （全体戦術方針、認識変容を促すコミュニケーション戦術の方向性、メディア・チャネル選定の条件、話題の増幅・連鎖の仕組みの要件。※生成AIの出力内容を正しい認識へと上書き（ハック）する視点を必ず考慮条件に含めること）

        ---
        ## 【別AIインプット用】WHO / WHAT / HOW 整理
        このプロジェクトを別のAI（企画立案用AI）に引き継ぐための要件整理として、以下の項目を記述してください。
        * **WHO**：ペルソナ像の定義／変容させるべき現在のインサイト／カスタマージャーニーにおける認識変化のポイント
        * **WHAT**：ブランドが定着させるべきポジショニング／POD（Point of Difference）／提案すべきプロポジション
        * **HOW**：認識変容を促すIMCテーマの方向性／施策の評価基準／KPI設計の考え方／予算配分の考え方（※具体的な施策案ではなく、企画時のガイドライン）
        """
        
        response = model.generate_content([prompt, uploaded_gemini_file])
        result_text = response.text
        
        genai.delete_file(uploaded_gemini_file.name)
        return result_text

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

def create_pdf(markdown_text):
    html_body = markdown.markdown(markdown_text, extensions=['tables'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
            
            @page {{
                size: A4;
                margin: 25mm 20mm;
                @bottom-right {{
                    content: counter(page);
                    font-family: 'Noto Sans JP', sans-serif;
                    font-size: 9pt;
                    color: #64748b;
                }}
            }}
            
            body {{
                font-family: 'Noto Sans JP', sans-serif;
                color: #334155;
                line-height: 1.8;
                font-size: 10.5pt;
                word-wrap: break-word;
            }}
            
            h1 {{ font-size: 20pt; color: #1A365D; text-align: center; border-bottom: 3px solid #26D0CE; padding-bottom: 12px; margin-bottom: 35px; font-weight: 700; }}
            h2 {{ font-size: 14pt; color: #1A365D; background-color: #F8FAFC; border-left: 6px solid #1A2980; padding: 10px 15px; margin-top: 40px; margin-bottom: 20px; font-weight: 700; page-break-after: avoid; }}
            h3 {{ font-size: 12pt; color: #2B6CB0; border-bottom: 1px dashed #CBD5E1; padding-bottom: 6px; margin-top: 25px; margin-bottom: 15px; font-weight: 700; page-break-after: avoid; }}
            p {{ margin-bottom: 15px; text-align: justify; }}
            ul, ol {{ margin-top: 5px; margin-bottom: 20px; padding-left: 25px; }}
            li {{ margin-bottom: 8px; }}
            strong {{ color: #1A2980; font-weight: 700; background: linear-gradient(transparent 70%, #E0F2FE 0%); }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 15px; margin-bottom: 25px; page-break-inside: avoid; }}
            th, td {{ border: 1px solid #E2E8F0; padding: 12px; text-align: left; }}
            th {{ background-color: #1A365D; color: white; font-weight: 500; }}
            tr:nth-child(even) {{ background-color: #F8FAFC; }}
            hr {{ border: none; border-top: 2px solid #E2E8F0; margin: 40px 0; }}
            blockquote {{ border-left: 4px solid #26D0CE; background-color: #F0FDFA; margin: 15px 0; padding: 12px 15px; color: #0F766E; }}
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
