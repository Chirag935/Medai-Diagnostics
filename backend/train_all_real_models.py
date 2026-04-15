#!/usr/bin/env python3
"""
Train All Medical Prediction Models using Real Datasets
"""

import os
import sys
import subprocess
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"EXECUTING: {description}")
    print(f"COMMAND: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(f"SUCCESS: {description}")
            print(result.stdout)
            return True
        else:
            print(f"FAILED: {description}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR running {description}: {e}")
        return False

def main():
    """Main training pipeline for all models"""
    print("="*80)
    print("MEDAI DIAGNOSTICS - COMPLETE MODEL TRAINING PIPELINE")
    print("Training All Models with Real Medical Datasets")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Training steps in order
    training_steps = [
        {
            'command': 'python download_datasets_fixed.py',
            'description': 'Download All Real Medical Datasets'
        },
        {
            'command': 'python train_real_diabetes_model.py',
            'description': 'Train Diabetes Prediction Model (Pima Indians Dataset)'
        },
        {
            'command': 'python train_real_breast_cancer_model.py',
            'description': 'Train Breast Cancer Prediction Model (WDBC Dataset)'
        },
        {
            'command': 'python train_heart_disease_model.py',
            'description': 'Train Heart Disease Prediction Model'
        },
        {
            'command': 'python train_liver_disease_model.py',
            'description': 'Train Liver Disease Prediction Model'
        },
        {
            'command': 'python train_kidney_disease_model.py',
            'description': 'Train Kidney Disease Prediction Model'
        },
        {
            'command': 'python train_alzheimer_model.py',
            'description': 'Train Alzheimer Prediction Model'
        },
        {
            'command': 'python train_pneumonia_model.py',
            'description': 'Train Pneumonia Detection Model'
        },
        {
            'command': 'python train_malaria_model.py',
            'description': 'Train Malaria Detection Model'
        }
    ]
    
    results = []
    
    for step in training_steps:
        success = run_command(step['command'], step['description'])
        results.append({
            'step': step['description'],
            'success': success
        })
        
        if not success:
            print(f"\nWARNING: {step['description']} failed. Continuing with next step...")
    
    # Summary
    print("\n" + "="*80)
    print("TRAINING PIPELINE SUMMARY")
    print("="*80)
    
    successful_steps = sum(1 for r in results if r['success'])
    total_steps = len(results)
    
    for result in results:
        status = "SUCCESS" if result['success'] else "FAILED"
        print(f"{result['step']}: {status}")
    
    print(f"\nOverall: {successful_steps}/{total_steps} steps completed successfully")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful_steps == total_steps:
        print("\nALL MODELS TRAINED SUCCESSFULLY!")
        print("Ready to start the application with real trained models.")
    else:
        print(f"\n{total_steps - successful_steps} steps failed.")
        print("Check the error messages above and retry failed steps.")
    
    return successful_steps == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
