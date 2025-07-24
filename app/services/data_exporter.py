# app/services/data_exporter.py
"""
Data Export Service for Talazo AgriFinance Platform.
"""

import os
import csv
import json
from datetime import datetime
from flask import current_app
from app.models import db, Farmer, SoilSample, LoanApplication, InsurancePolicy
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """Export platform data to various formats."""
    
    def __init__(self):
        self.export_dir = os.path.join(current_app.root_path, '..', 'exports')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_all_data(self):
        """Export all data to CSV files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        exports = {
            'farmers': self.export_farmers(timestamp),
            'soil_samples': self.export_soil_samples(timestamp),
            'loan_applications': self.export_loan_applications(timestamp),
            'insurance_policies': self.export_insurance_policies(timestamp)
        }
        
        # Create summary file
        summary_path = os.path.join(self.export_dir, f'export_summary_{timestamp}.json')
        with open(summary_path, 'w') as f:
            json.dump({
                'export_timestamp': timestamp,
                'files_created': exports,
                'total_records': sum(exports.values())
            }, f, indent=2)
        
        logger.info(f"Data export completed. Summary: {summary_path}")
        return exports
    
    def export_farmers(self, timestamp=None):
        """Export farmers data to CSV."""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f'farmers_{timestamp}.csv'
        filepath = os.path.join(self.export_dir, filename)
        
        farmers = Farmer.query.all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'name', 'email', 'phone_number', 'national_id',
                'farm_size_hectares', 'location', 'crop_type',
                'farming_experience_years', 'created_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for farmer in farmers:
                writer.writerow({
                    'id': farmer.id,
                    'name': farmer.name,
                    'email': farmer.email,
                    'phone_number': farmer.phone_number,
                    'national_id': farmer.national_id,
                    'farm_size_hectares': farmer.farm_size_hectares,
                    'location': farmer.location,
                    'crop_type': farmer.crop_type.value if farmer.crop_type else '',
                    'farming_experience_years': farmer.farming_experience_years,
                    'created_at': farmer.created_at.isoformat() if farmer.created_at else ''
                })
        
        logger.info(f"Exported {len(farmers)} farmers to {filepath}")
        return len(farmers)
    
    def export_soil_samples(self, timestamp=None):
        """Export soil samples data to CSV."""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f'soil_samples_{timestamp}.csv'
        filepath = os.path.join(self.export_dir, filename)
        
        samples = SoilSample.query.all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'farmer_id', 'collection_date', 'ph_level',
                'nitrogen_level', 'phosphorus_level', 'potassium_level',
                'organic_matter', 'moisture_content', 'financial_index_score',
                'risk_level', 'created_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for sample in samples:
                writer.writerow({
                    'id': sample.id,
                    'farmer_id': sample.farmer_id,
                    'collection_date': sample.collection_date.isoformat() if sample.collection_date else '',
                    'ph_level': sample.ph_level,
                    'nitrogen_level': sample.nitrogen_level,
                    'phosphorus_level': sample.phosphorus_level,
                    'potassium_level': sample.potassium_level,
                    'organic_matter': sample.organic_matter,
                    'moisture_content': sample.moisture_content,
                    'financial_index_score': sample.financial_index_score,
                    'risk_level': sample.risk_level.value if sample.risk_level else '',
                    'created_at': sample.created_at.isoformat() if sample.created_at else ''
                })
        
        logger.info(f"Exported {len(samples)} soil samples to {filepath}")
        return len(samples)
    
    def export_loan_applications(self, timestamp=None):
        """Export loan applications data to CSV."""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f'loan_applications_{timestamp}.csv'
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            applications = LoanApplication.query.all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'farmer_id', 'amount_requested', 'purpose',
                    'status', 'application_date', 'decision_date',
                    'approved_amount', 'interest_rate'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for app in applications:
                    writer.writerow({
                        'id': app.id,
                        'farmer_id': app.farmer_id,
                        'amount_requested': app.amount_requested,
                        'purpose': app.purpose,
                        'status': app.status.value if app.status else '',
                        'application_date': app.application_date.isoformat() if app.application_date else '',
                        'decision_date': app.decision_date.isoformat() if app.decision_date else '',
                        'approved_amount': app.approved_amount,
                        'interest_rate': app.interest_rate
                    })
            
            logger.info(f"Exported {len(applications)} loan applications to {filepath}")
            return len(applications)
        except Exception as e:
            logger.warning(f"Could not export loan applications: {e}")
            return 0
    
    def export_insurance_policies(self, timestamp=None):
        """Export insurance policies data to CSV."""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f'insurance_policies_{timestamp}.csv'
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            policies = InsurancePolicy.query.all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'farmer_id', 'policy_type', 'coverage_amount',
                    'premium_amount', 'start_date', 'end_date',
                    'status', 'created_at'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for policy in policies:
                    writer.writerow({
                        'id': policy.id,
                        'farmer_id': policy.farmer_id,
                        'policy_type': policy.policy_type,
                        'coverage_amount': policy.coverage_amount,
                        'premium_amount': policy.premium_amount,
                        'start_date': policy.start_date.isoformat() if policy.start_date else '',
                        'end_date': policy.end_date.isoformat() if policy.end_date else '',
                        'status': policy.status.value if policy.status else '',
                        'created_at': policy.created_at.isoformat() if policy.created_at else ''
                    })
            
            logger.info(f"Exported {len(policies)} insurance policies to {filepath}")
            return len(policies)
        except Exception as e:
            logger.warning(f"Could not export insurance policies: {e}")
            return 0
