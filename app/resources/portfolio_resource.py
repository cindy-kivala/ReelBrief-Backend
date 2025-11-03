"""
Portfolio API Routes with Payment Integration
Owner: Caleb (Portfolio display and management)
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

# Core portfolio imports
from app.services.portfolio_service import PortfolioService
from app.models.portfolio_item import PortfolioItem
from app.extensions import db

# Payment/Wallet imports
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.escrow_transaction import EscrowTransaction
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.user import User
from app.services.email_service import send_email, send_funds_released_email

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')

@portfolio_bp.route('/freelancer/<int:freelancer_id>', methods=['GET'])
def get_public_portfolio(freelancer_id):
    """
    Public endpoint - Get freelancer's portfolio with profile (only visible items)
    Includes payment/earnings summary if available
    """
    try:
        data = PortfolioService.get_freelancer_portfolio_with_profile(
            freelancer_id,
            include_hidden=False
        )
        
        if not data:
            return jsonify({"error": "Freelancer portfolio not found"}), 404
        
        # Add payment/earnings information
        try:
            # Get freelancer's total earnings from wallet transactions
            freelancer_wallet = Wallet.query.filter_by(user_id=freelancer_id).first()
            if freelancer_wallet:
                total_earnings = db.session.query(
                    db.func.sum(WalletTransaction.amount)
                ).filter(
                    WalletTransaction.wallet_id == freelancer_wallet.id,
                    WalletTransaction.transaction_type.in_(['release', 'credit'])
                ).scalar() or 0
                
                data['payment_summary'] = {
                    'total_earnings': float(total_earnings),
                    'wallet_balance': float(freelancer_wallet.balance),
                    'currency': freelancer_wallet.currency
                }
        except Exception as payment_error:
            # Don't fail if payment data can't be loaded
            print(f"Payment data load error: {payment_error}")
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/me/earnings', methods=['GET'])
@jwt_required()
def get_my_earnings():
    """
    Get current freelancer's earnings and payment history
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get wallet and transactions
        wallet = Wallet.query.filter_by(user_id=current_user_id).first()
        if not wallet:
            return jsonify({"error": "Wallet not found"}), 404
        
        # Get earnings transactions
        earnings_transactions = WalletTransaction.query.filter(
            WalletTransaction.wallet_id == wallet.id,
            WalletTransaction.transaction_type.in_(['release', 'credit', 'payment_release'])
        ).order_by(WalletTransaction.created_at.desc()).all()
        
        # Get pending escrow amounts
        pending_escrow = EscrowTransaction.query.filter(
            EscrowTransaction.receiver_id == current_user_id,
            EscrowTransaction.status == 'held'
        ).all()
        
        total_pending = sum(float(escrow.amount) for escrow in pending_escrow)
        
        return jsonify({
            "wallet_balance": float(wallet.balance),
            "total_earnings": float(sum(tx.amount for tx in earnings_transactions)),
            "pending_earnings": total_pending,
            "currency": wallet.currency,
            "recent_transactions": [tx.to_dict() for tx in earnings_transactions[:10]],
            "pending_payments": [escrow.to_dict() for escrow in pending_escrow]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@portfolio_bp.route('/project/<int:project_id>/payment-status', methods=['GET'])
@jwt_required()
def get_project_payment_status(project_id):
    """
    Get payment status for a specific project in portfolio
    """
    try:
        current_user_id = get_jwt_identity()
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Verify user owns this project
        if project.freelancer_id != current_user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get escrow transactions for this project
        escrow_transactions = EscrowTransaction.query.filter_by(
            project_id=project_id
        ).order_by(EscrowTransaction.created_at.desc()).all()
        
        # Get related invoices
        invoices = Invoice.query.filter_by(project_id=project_id).all()
        
        payment_status = {
            "project_id": project_id,
            "project_title": project.title,
            "budget": float(project.budget) if project.budget else 0,
            "escrow_transactions": [escrow.to_dict() for escrow in escrow_transactions],
            "invoices": [invoice.to_dict() for invoice in invoices],
            "total_released": sum(
                float(escrow.amount) 
                for escrow in escrow_transactions 
                if escrow.status == 'released'
            ),
            "total_held": sum(
                float(escrow.amount) 
                for escrow in escrow_transactions 
                if escrow.status == 'held'
            )
        }
        
        return jsonify(payment_status), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500