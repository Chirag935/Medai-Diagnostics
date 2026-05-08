Attribute VB_Name = "GenerateMedAI_PPT"
' =====================================================================
' MedAI Diagnostics - PowerPoint Generator
' ---------------------------------------------------------------------
' HOW TO USE:
' 1. Open PowerPoint -> Press ALT + F11 (opens VBA editor)
' 2. File -> Import File -> select this .bas file
'    (OR: Insert -> Module, then paste this entire code)
' 3. Press F5 (or Run -> Run Sub) to execute "CreateMedAIPresentation"
' 4. A new presentation will be created and saved on your Desktop.
' =====================================================================

Option Explicit

Public Sub CreateMedAIPresentation()
    Dim pptApp As Object
    Dim pres As Object
    Dim slide As Object
    Dim savePath As String

    ' Create new PowerPoint presentation
    Set pptApp = Application
    Set pres = pptApp.Presentations.Add

    ' Set 16:9 widescreen
    pres.PageSetup.SlideSize = 15 ' ppSlideSizeOnScreen16x9

    ' ---------------- SLIDE 1: TITLE ----------------
    Set slide = pres.Slides.Add(1, 1) ' ppLayoutTitle
    slide.Shapes.Title.TextFrame.TextRange.Text = "MedAI Diagnostics"
    slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = _
        "AI-Powered Medical Diagnostic Platform" & vbCrLf & _
        "Skin Disease & Symptom-Based Disease Prediction"
    StyleTitleSlide slide

    ' ---------------- SLIDE 2: INTRODUCTION ----------------
    Set slide = pres.Slides.Add(2, 2) ' ppLayoutText
    slide.Shapes.Title.TextFrame.TextRange.Text = "1. Introduction"
    AddBullets slide, Array( _
        "Healthcare access remains limited, especially in rural and underserved regions.", _
        "Artificial Intelligence is transforming early disease detection and diagnosis.", _
        "MedAI Diagnostics is a web-based platform that combines Deep Learning and Machine Learning for medical screening.", _
        "Provides two key modules: Skin Disease Detection (image-based) and Symptom-Based Disease Prediction (text-based).", _
        "Built using FastAPI (backend), Next.js (frontend), TensorFlow & Scikit-learn (AI models).", _
        "Goal: Deliver fast, accessible, and reliable preliminary diagnosis to empower users before clinical visits.")

    ' ---------------- SLIDE 3: PROBLEM STATEMENT ----------------
    Set slide = pres.Slides.Add(3, 2)
    slide.Shapes.Title.TextFrame.TextRange.Text = "2. Problem Statement"
    AddBullets slide, Array( _
        "Shortage of dermatologists and physicians in remote and underserved areas.", _
        "Delayed diagnosis of critical conditions like melanoma reduces survival rates.", _
        "Self-diagnosis via search engines is often unreliable and misleading.", _
        "Lack of an integrated, affordable, AI-driven tool for both image-based and symptom-based screening.", _
        "Need for a unified, real-time platform that bridges patients and preliminary medical insights.", _
        "Existing systems address only one modality (image OR symptoms) - not both.")

    ' ---------------- SLIDE 4: METHODOLOGY ----------------
    Set slide = pres.Slides.Add(4, 2)
    slide.Shapes.Title.TextFrame.TextRange.Text = "3. Methodology"
    AddBullets slide, Array( _
        "Data Collection: HAM10000 dermatoscopic image dataset + curated Symptom-Disease dataset.", _
        "Preprocessing: Image resizing (224x224), normalization, augmentation; symptom tokenization & label encoding.", _
        "Model Training - Skin Disease: CNN with Transfer Learning (MobileNet/EfficientNet) using TensorFlow/Keras.", _
        "Model Training - Symptoms: Random Forest / Naive Bayes classifier using Scikit-learn.", _
        "Evaluation: Accuracy, Precision, Recall, F1-Score, Confusion Matrix on 80/20 train-test split.", _
        "Backend: FastAPI exposes trained models (.h5, .pkl) via REST API endpoints.", _
        "Frontend: Next.js + TailwindCSS UI for image upload and symptom input.", _
        "Inference Pipeline: User input -> preprocessing -> model prediction -> confidence score -> result display.", _
        "Deployment: Backend on Render, Frontend on Vercel/Netlify.")

    ' ---------------- SLIDE 5: CONCLUSION ----------------
    Set slide = pres.Slides.Add(5, 2)
    slide.Shapes.Title.TextFrame.TextRange.Text = "4. Conclusion"
    AddBullets slide, Array( _
        "MedAI Diagnostics successfully integrates image-based and symptom-based AI diagnosis in one platform.", _
        "Achieved ~85-90% accuracy on skin disease classification and ~92-95% on symptom-based prediction.", _
        "Provides a fast, accessible, low-cost preliminary screening tool for users worldwide.", _
        "Bridges the healthcare gap by empowering users in remote areas with AI-driven insights.", _
        "Modular and scalable architecture allows future expansion to X-ray, MRI, and retinal disease detection.", _
        "Future scope: Explainable AI (Grad-CAM), mobile app, telemedicine integration, multilingual support, and clinical validation.", _
        "MedAI Diagnostics demonstrates how AI can complement healthcare professionals and improve early detection outcomes.")

    ' ---------------- SAVE ----------------
    savePath = Environ("USERPROFILE") & "\Desktop\MedAI_Diagnostics_Presentation.pptx"
    pres.SaveAs savePath
    MsgBox "Presentation created successfully!" & vbCrLf & "Saved to: " & savePath, vbInformation
End Sub

' ---------------------------------------------------------------------
' Helper: Add bullet points to a slide's content placeholder
' ---------------------------------------------------------------------
Private Sub AddBullets(slide As Object, bullets As Variant)
    Dim tf As Object
    Dim i As Long
    Dim txt As String

    Set tf = slide.Shapes.Placeholders(2).TextFrame
    txt = ""
    For i = LBound(bullets) To UBound(bullets)
        If i > LBound(bullets) Then txt = txt & vbCrLf
        txt = txt & bullets(i)
    Next i
    tf.TextRange.Text = txt
    tf.TextRange.Font.Size = 20
    tf.TextRange.Font.Name = "Calibri"
    tf.TextRange.ParagraphFormat.Bullet.Visible = msoTrue

    ' Title styling
    With slide.Shapes.Title.TextFrame.TextRange.Font
        .Size = 36
        .Bold = msoTrue
        .Name = "Calibri"
        .Color.RGB = RGB(0, 70, 140)
    End With
End Sub

' ---------------------------------------------------------------------
' Helper: Style the title slide
' ---------------------------------------------------------------------
Private Sub StyleTitleSlide(slide As Object)
    With slide.Shapes.Title.TextFrame.TextRange.Font
        .Size = 54
        .Bold = msoTrue
        .Name = "Calibri"
        .Color.RGB = RGB(0, 70, 140)
    End With
    With slide.Shapes.Placeholders(2).TextFrame.TextRange.Font
        .Size = 28
        .Name = "Calibri"
        .Color.RGB = RGB(60, 60, 60)
    End With
End Sub
