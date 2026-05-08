Attribute VB_Name = "GeneratePPT"
'==============================================================================
' MedAI Diagnostics - PowerPoint Auto-Generator
'==============================================================================
' HOW TO USE:
'   1. Open PowerPoint -> press ALT + F11 to open the VBA editor.
'   2. In the menu: Insert -> Module.
'   3. Paste this entire file into the new module.
'   4. Edit the constants below (YOUR_NAME, YOUR_USN, GUIDE_NAME, etc.).
'   5. Press F5 (or Run -> Run Sub).
'   6. A complete 15-slide deck will be generated.
'   7. Save as .pptx.
'==============================================================================

Option Explicit

' ============ EDIT THESE BEFORE RUNNING ============
Const YOUR_NAME As String = "[YOUR FULL NAME]"
Const YOUR_USN As String = "[YOUR USN]"
Const GUIDE_NAME As String = "[Prof. / Dr. GUIDE NAME]"
Const DEPARTMENT As String = "[DEPARTMENT]"
Const COLLEGE_NAME As String = "[COLLEGE NAME]"
Const ACADEMIC_YEAR As String = "[ACADEMIC YEAR]"
' ====================================================

' Theme colors (dark theme with teal accent)
Const CLR_BG As Long = &H180A05         ' #050a18 dark navy
Const CLR_TITLE As Long = &HFFFFFF      ' white
Const CLR_BODY As Long = &HE5E5E5       ' light gray
Const CLR_ACCENT As Long = &HB68214     ' teal #14b886 (BGR)
Const CLR_FOOTER As Long = &H808080     ' gray

Sub GenerateMedAIDeck()
    Dim pres As Presentation
    Set pres = Application.Presentations.Add
    pres.PageSetup.SlideSize = ppSlideSizeOnScreen16x9

    ' Build slides
    AddTitleSlide pres
    AddContentSlide pres, "Presentation Outline", _
        "Introduction" & vbCrLf & _
        "Problem Statement & Objectives" & vbCrLf & _
        "Existing Systems" & vbCrLf & _
        "Proposed System" & vbCrLf & _
        "Methodology" & vbCrLf & _
        "System Architecture" & vbCrLf & _
        "Implementation" & vbCrLf & _
        "Module-wise Explanation" & vbCrLf & _
        "Results & Performance" & vbCrLf & _
        "Live Demo" & vbCrLf & _
        "Conclusion & Future Scope"

    AddContentSlide pres, "Introduction", _
        "Healthcare in low-resource regions suffers from specialist shortages, especially in dermatology - around 3 billion people lack timely access." & vbCrLf & _
        "Modern AI can perform medical screening tasks competitively when trained on benchmark datasets." & vbCrLf & _
        "MedAI Diagnostics is a full-stack platform integrating THREE real machine learning models: Random Forest, CNN, and LLM." & vbCrLf & _
        "Serves three roles: Patient, Doctor, Receptionist - with role-based access control." & vbCrLf & _
        "Provides explainable AI with Grad-CAM heatmaps, an LLM-powered medical assistant, EMR system, appointments, and offline medication reminders." & vbCrLf & _
        "Positioned as a decision-SUPPORT tool, never a doctor replacement, with built-in safety disclaimers."

    AddContentSlide pres, "Problem Statement & Objectives", _
        "PROBLEM:" & vbCrLf & _
        "  - Limited access to specialists in tier-2 / tier-3 cities." & vbCrLf & _
        "  - Existing symptom checkers are generic and not personalized." & vbCrLf & _
        "  - Most student AI projects ship one model with no clinical workflow." & vbCrLf & _
        "  - Black-box predictions are not trusted in healthcare." & vbCrLf & _
        "" & vbCrLf & _
        "OBJECTIVES:" & vbCrLf & _
        "  - Build a deployable multi-role medical platform." & vbCrLf & _
        "  - Train real ML models on benchmark datasets, not toy data." & vbCrLf & _
        "  - Provide explainable AI: heatmaps and class probabilities." & vbCrLf & _
        "  - Integrate a GenAI assistant with retrieval-augmented context." & vbCrLf & _
        "  - Implement an MLOps feedback loop for continuous improvement." & vbCrLf & _
        "  - Support multilingual and offline-first workflow."

    AddContentSlide pres, "Existing Systems & Limitations", _
        "SkinVision: Mobile skin scanning - Closed-source, paid, single-feature only." & vbCrLf & _
        "Ada Health: Symptom checker - Generic, no role-based workflow." & vbCrLf & _
        "First Derm: Telemedicine - Human-in-loop only, costly, no AI." & vbCrLf & _
        "Buoy Health: Conversational symptoms - No imaging, no MLOps." & vbCrLf & _
        "" & vbCrLf & _
        "MedAI Diagnostics (Proposed):" & vbCrLf & _
        "  - 3 AI models in one platform (RF + CNN + LLM)" & vbCrLf & _
        "  - Multi-role workflow (Patient / Doctor / Receptionist)" & vbCrLf & _
        "  - MLOps feedback loop for continuous learning" & vbCrLf & _
        "  - Offline-first medication reminders" & vbCrLf & _
        "  - Multilingual interface (English + Hindi)"

    AddContentSlide pres, "Proposed System", _
        "A unified web platform integrating three independent AI engines behind a role-aware frontend." & vbCrLf & _
        "" & vbCrLf & _
        "ENGINE 1 - Tabular ML:" & vbCrLf & _
        "  Random Forest classifier - 132 symptoms map to 41 diseases." & vbCrLf & _
        "  ~99% accuracy on academic dataset." & vbCrLf & _
        "" & vbCrLf & _
        "ENGINE 2 - Computer Vision:" & vbCrLf & _
        "  MobileNetV2 CNN - 7-class skin lesion classifier." & vbCrLf & _
        "  Trained on HAM10000 (10,015 images)." & vbCrLf & _
        "  74.59% validation accuracy with Grad-CAM explainability." & vbCrLf & _
        "" & vbCrLf & _
        "ENGINE 3 - Generative AI:" & vbCrLf & _
        "  Llama 3.3 70B via Groq, Retrieval-Augmented Generation (RAG)." & vbCrLf & _
        "  Grounds responses in user's actual diagnostic context."

    AddContentSlide pres, "Methodology", _
        "1. DATA ACQUISITION - HAM10000 dataset (skin), Symptom-Disease 4920-record dataset." & vbCrLf & _
        "2. PREPROCESSING - Image resize to 224x224, normalization, augmentation." & vbCrLf & _
        "3. MODEL SELECTION - MobileNetV2 (CNN), Random Forest (RF), Llama 3.3 (LLM)." & vbCrLf & _
        "4. TRAINING STRATEGY - Two-stage transfer learning:" & vbCrLf & _
        "      Stage 1: 10 epochs head-only training (LR = 1e-3)." & vbCrLf & _
        "      Stage 2: 15 epochs fine-tuning top 50 layers (LR = 1e-5)." & vbCrLf & _
        "5. CLASS IMBALANCE HANDLING - sklearn compute_class_weight='balanced'." & vbCrLf & _
        "      (HAM10000 is 67% nv class - balancing prevents trivial majority prediction.)" & vbCrLf & _
        "6. EVALUATION - 80/20 stratified split, validation accuracy as primary metric." & vbCrLf & _
        "7. DEPLOYMENT - FastAPI backend + Next.js 14 frontend on Render." & vbCrLf & _
        "8. MLOPS - Predictions auto-logged to Supabase, user feedback closes the loop."

    AddContentSlide pres, "Methodology - Skin Lesion Classifier Pipeline", _
        "HAM10000 (10,015 images)" & vbCrLf & _
        "        |" & vbCrLf & _
        "Stratified 80/20 train-val split" & vbCrLf & _
        "        |" & vbCrLf & _
        "Augmentation (flip, rotate, hue, saturation, brightness)" & vbCrLf & _
        "        |" & vbCrLf & _
        "MobileNetV2 (ImageNet pretrained, frozen)" & vbCrLf & _
        "        |" & vbCrLf & _
        "Custom Dense Head (Dropout + Softmax over 7 classes)" & vbCrLf & _
        "        |" & vbCrLf & _
        "Stage-1: Train head only (10 epochs)" & vbCrLf & _
        "        |" & vbCrLf & _
        "Stage-2: Unfreeze top 50 layers, fine-tune (15 epochs)" & vbCrLf & _
        "        |" & vbCrLf & _
        "Callbacks: ReduceLROnPlateau + EarlyStopping" & vbCrLf & _
        "        |" & vbCrLf & _
        "Inference -> Softmax probabilities + Grad-CAM heatmap"

    AddContentSlide pres, "System Architecture", _
        "USER LAYER" & vbCrLf & _
        "  Patient | Doctor | Receptionist  (Role-Based Access Control)" & vbCrLf & _
        "                       |" & vbCrLf & _
        "FRONTEND" & vbCrLf & _
        "  Next.js 14 + TypeScript + TailwindCSS" & vbCrLf & _
        "  AuthContext, LanguageContext, react-three-fiber 3D body map" & vbCrLf & _
        "                       |" & vbCrLf & _
        "API GATEWAY" & vbCrLf & _
        "  FastAPI + slowapi rate limiting + CORS middleware" & vbCrLf & _
        "                       |" & vbCrLf & _
        "AI ENGINES" & vbCrLf & _
        "  Symptom RF (sklearn) | Skin CNN (TensorFlow) | RAG Chat (Groq -> Llama 3.3)" & vbCrLf & _
        "                       |" & vbCrLf & _
        "DATA LAYER" & vbCrLf & _
        "  Supabase (Postgres) - users, predictions, feedback, appointments" & vbCrLf & _
        "  localStorage - medication reminders (offline-first)"

    AddContentSlide pres, "Implementation - Technology Stack", _
        "Frontend: Next.js 14 (App Router) + TypeScript + TailwindCSS + react-three-fiber" & vbCrLf & _
        "Backend: FastAPI + Pydantic + Uvicorn (Python 3.11)" & vbCrLf & _
        "Tabular ML: scikit-learn (Random Forest)" & vbCrLf & _
        "Deep Learning: TensorFlow / Keras 2.15 (MobileNetV2)" & vbCrLf & _
        "Computer Vision: OpenCV (preprocessing + Grad-CAM heatmap)" & vbCrLf & _
        "LLM: Llama 3.3 70B via Groq API (free tier, ~500 tokens/sec)" & vbCrLf & _
        "Database: Supabase (Postgres) - auth, predictions, EMR" & vbCrLf & _
        "PDF Export: jsPDF + html2canvas (client-side prescription PDFs)" & vbCrLf & _
        "Rate Limiting: slowapi (Starlette compatible)" & vbCrLf & _
        "Deployment: Render (backend) + Vercel-ready frontend" & vbCrLf & _
        "Build Tools: render.yaml, Procfile, start.bat (single-command boot)"

    AddContentSlide pres, "Implementation - Modules Built", _
        "AI MODULES (Backend Routers):" & vbCrLf & _
        "  - symptom_checker.py - RF inference + 41-disease descriptions" & vbCrLf & _
        "  - skin_analyzer.py - CNN inference + Grad-CAM + OpenCV fallback" & vbCrLf & _
        "  - chat.py - RAG chatbot (Groq) + offline rule-based fallback" & vbCrLf & _
        "" & vbCrLf & _
        "HEALTHCARE WORKFLOW MODULES:" & vbCrLf & _
        "  - patients.py - Multi-role auth + patient EMR CRUD" & vbCrLf & _
        "  - appointments.py - Scheduling, requests, role checks" & vbCrLf & _
        "  - feedback.py - Prediction logging + accuracy feedback" & vbCrLf & _
        "  - metrics.py - Live model status for MLOps dashboard" & vbCrLf & _
        "" & vbCrLf & _
        "FRONTEND PAGES (9 total):" & vbCrLf & _
        "  Home, Login, Symptom Checker, Skin Analyzer, AI Assistant," & vbCrLf & _
        "  Medication Reminders, Patients EMR, Prescription, Appointments, MLOps Dashboard"

    AddContentSlide pres, "Explanation - How the System Delivers Value", _
        "1. EXPLAINABLE AI" & vbCrLf & _
        "  - Every CNN prediction returns full 7-class probability distribution." & vbCrLf & _
        "  - Grad-CAM heatmap shows WHICH PIXELS the model used." & vbCrLf & _
        "  - Doctors can audit predictions for trust and clinical safety." & vbCrLf & _
        "" & vbCrLf & _
        "2. RETRIEVAL-AUGMENTED GENERATION (RAG)" & vbCrLf & _
        "  - Diagnostic context injected as system message before user prompt." & vbCrLf & _
        "  - Without RAG: 'Consult a doctor.' (generic)" & vbCrLf & _
        "  - With RAG: 'Based on your Melanoma 78% prediction, schedule a" & vbCrLf & _
        "    dermoscopic exam and apply the ABCDE rule...' (personalized)" & vbCrLf & _
        "" & vbCrLf & _
        "3. GRACEFUL DEGRADATION" & vbCrLf & _
        "  - TF unavailable -> OpenCV fallback engine." & vbCrLf & _
        "  - Groq API down -> local rule-based chatbot." & vbCrLf & _
        "  - Supabase offline -> medication reminders still work via localStorage."

    AddContentSlide pres, "Results & Performance", _
        "PERFORMANCE METRICS:" & vbCrLf & _
        "" & vbCrLf & _
        "Skin CNN - Validation Accuracy: 74.59 %" & vbCrLf & _
        "Skin CNN - Random baseline: 14.3 %  (1/7)" & vbCrLf & _
        "Skin CNN - Majority-class baseline: 67 %  (always predict 'nv')" & vbCrLf & _
        "Skin CNN - Inference Latency (CPU): less than 1.5 sec" & vbCrLf & _
        "Skin CNN - Model Size: 26 MB (.h5)" & vbCrLf & _
        "Skin CNN - Training Time (CPU): ~ 45 minutes" & vbCrLf & _
        "" & vbCrLf & _
        "Symptom RF - Test Accuracy: ~ 99 %" & vbCrLf & _
        "Symptom RF - Inference Latency: less than 100 ms" & vbCrLf & _
        "" & vbCrLf & _
        "RAG Chat - Response Latency: 1 - 2 seconds" & vbCrLf & _
        "" & vbCrLf & _
        "KEY INSIGHT:" & vbCrLf & _
        "Beats random baseline by 60+ points and majority-class by 7+ points." & vbCrLf & _
        "Model genuinely learns minority classes - including melanoma."

    AddContentSlide pres, "Live Demo", _
        "" & vbCrLf & _
        "[ Skin Analyzer with Grad-CAM heatmap ]" & vbCrLf & _
        "" & vbCrLf & _
        "[ Symptom Checker with 3D body map ]" & vbCrLf & _
        "" & vbCrLf & _
        "[ RAG Chatbot with diagnostic context ]" & vbCrLf & _
        "" & vbCrLf & _
        "[ MLOps Dashboard with live metrics ]" & vbCrLf & _
        "" & vbCrLf & _
        "==> Switch to live application now."

    AddContentSlide pres, "Conclusion & Future Scope", _
        "CONCLUSION:" & vbCrLf & _
        "  - Built a deployable medical AI platform with 3 real models." & vbCrLf & _
        "  - Achieved 74.59% validation accuracy on 7-class skin classification." & vbCrLf & _
        "  - Beat majority-class baseline by 7+ points - learns minority classes." & vbCrLf & _
        "  - Implemented Explainable AI, MLOps loop, RBAC, graceful degradation." & vbCrLf & _
        "  - Demonstrated end-to-end full-stack capability: ML, API, UI, DevOps." & vbCrLf & _
        "" & vbCrLf & _
        "FUTURE SCOPE:" & vbCrLf & _
        "  - GPU-trained skin CNN at 85%+ (EfficientNetB3 / ResNet50)." & vbCrLf & _
        "  - Demographic fairness audit using Fitzpatrick17k dataset." & vbCrLf & _
        "  - Mobile app via React Native." & vbCrLf & _
        "  - HIPAA hardening + FDA Class II clearance pathway." & vbCrLf & _
        "  - Federated learning across partner clinics." & vbCrLf & _
        "  - Add TB chest X-ray module (second CNN)." & vbCrLf & _
        "  - Drug-interaction checker via RxNav API." & vbCrLf & _
        "" & vbCrLf & _
        "                                Thank You. Questions?"

    ' Remove the default blank slide PowerPoint adds at index 1
    On Error Resume Next
    If pres.Slides.Count > 15 Then
        Dim i As Integer
        For i = pres.Slides.Count To 16 Step -1
            pres.Slides(i).Delete
        Next i
    End If
    On Error GoTo 0

    MsgBox "MedAI Diagnostics deck generated successfully!" & vbCrLf & _
           "Total slides: " & pres.Slides.Count & vbCrLf & vbCrLf & _
           "Next steps:" & vbCrLf & _
           "1. Replace screenshot placeholders on Slide 14." & vbCrLf & _
           "2. Save as .pptx (and also export as .pdf for backup).", _
           vbInformation, "MedAI Generator"
End Sub

'------------------------------------------------------------------------------
' Helper: Title slide
'------------------------------------------------------------------------------
Private Sub AddTitleSlide(pres As Presentation)
    Dim sld As Slide
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    ApplyBackground sld

    ' Main title
    Dim shpTitle As Shape
    Set shpTitle = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 60, 120, 840, 80)
    With shpTitle.TextFrame.TextRange
        .Text = "MedAI Diagnostics"
        .Font.Size = 54
        .Font.Bold = msoTrue
        .Font.Color.RGB = CLR_TITLE
        .Font.Name = "Segoe UI"
    End With

    ' Accent line
    Dim shpLine As Shape
    Set shpLine = sld.Shapes.AddShape(msoShapeRectangle, 60, 210, 120, 4)
    shpLine.Fill.ForeColor.RGB = CLR_ACCENT
    shpLine.Line.Visible = msoFalse

    ' Subtitle
    Dim shpSub As Shape
    Set shpSub = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 60, 230, 840, 50)
    With shpSub.TextFrame.TextRange
        .Text = "An AI-Powered Multi-Role Medical Platform with Explainable Deep Learning"
        .Font.Size = 22
        .Font.Color.RGB = CLR_BODY
        .Font.Name = "Segoe UI Light"
    End With

    ' Author info block
    Dim shpAuthor As Shape
    Set shpAuthor = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 60, 340, 840, 180)
    With shpAuthor.TextFrame.TextRange
        .Text = "Submitted by: " & YOUR_NAME & vbCrLf & _
                "USN: " & YOUR_USN & vbCrLf & vbCrLf & _
                "Under the Guidance of: " & GUIDE_NAME
        .Font.Size = 22
        .Font.Color.RGB = CLR_TITLE
        .Font.Name = "Segoe UI"
    End With

    ' Footer
    Dim shpFoot As Shape
    Set shpFoot = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 60, 510, 840, 30)
    With shpFoot.TextFrame.TextRange
        .Text = DEPARTMENT & "  |  " & COLLEGE_NAME & "  |  " & ACADEMIC_YEAR
        .Font.Size = 14
        .Font.Color.RGB = CLR_FOOTER
        .Font.Name = "Segoe UI"
    End With
End Sub

'------------------------------------------------------------------------------
' Helper: Generic content slide with title + body
'------------------------------------------------------------------------------
Private Sub AddContentSlide(pres As Presentation, title As String, body As String)
    Dim sld As Slide
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    ApplyBackground sld

    ' Slide title
    Dim shpTitle As Shape
    Set shpTitle = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 50, 30, 860, 50)
    With shpTitle.TextFrame.TextRange
        .Text = title
        .Font.Size = 30
        .Font.Bold = msoTrue
        .Font.Color.RGB = CLR_TITLE
        .Font.Name = "Segoe UI"
    End With

    ' Accent underline
    Dim shpLine As Shape
    Set shpLine = sld.Shapes.AddShape(msoShapeRectangle, 50, 85, 80, 3)
    shpLine.Fill.ForeColor.RGB = CLR_ACCENT
    shpLine.Line.Visible = msoFalse

    ' Body content
    Dim shpBody As Shape
    Set shpBody = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 50, 110, 860, 420)
    With shpBody.TextFrame
        .WordWrap = msoTrue
        .TextRange.Text = body
        .TextRange.Font.Size = 16
        .TextRange.Font.Color.RGB = CLR_BODY
        .TextRange.Font.Name = "Segoe UI"
        .TextRange.ParagraphFormat.SpaceAfter = 4
    End With

    ' Footer
    Dim shpFoot As Shape
    Set shpFoot = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 50, 540, 860, 25)
    With shpFoot.TextFrame.TextRange
        .Text = "MedAI Diagnostics  |  " & YOUR_NAME & "  |  " & YOUR_USN
        .Font.Size = 11
        .Font.Color.RGB = CLR_FOOTER
        .Font.Name = "Segoe UI"
    End With
End Sub

'------------------------------------------------------------------------------
' Helper: Apply dark background to a slide
'------------------------------------------------------------------------------
Private Sub ApplyBackground(sld As Slide)
    sld.FollowMasterBackground = msoFalse
    sld.Background.Fill.Solid
    sld.Background.Fill.ForeColor.RGB = CLR_BG
End Sub
