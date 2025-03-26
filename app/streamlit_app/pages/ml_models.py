import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from app.ml.model_manager import ModelManager
from app.ml.feature_engineer import FeatureEngineer
from app.trading.exchange_client import ExchangeClient
import time

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def get_model_manager():
    """Get model manager instance."""
    return ModelManager()

@st.cache_resource(ttl=300)
def get_feature_engineer():
    """Get feature engineer instance."""
    return FeatureEngineer()

@st.cache_resource(ttl=300)
def get_exchange_client():
    """Get exchange client instance."""
    return ExchangeClient()

@st.cache_data(ttl=300)
def get_models():
    """Get list of models."""
    try:
        model_manager = get_model_manager()
        return model_manager.get_models()
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return None

@st.cache_data(ttl=300)
def get_model_metrics(model_id):
    """Get model metrics."""
    try:
        model_manager = get_model_manager()
        return model_manager.get_model_metrics(model_id)
    except Exception as e:
        logger.error(f"Error getting model metrics: {e}")
        return None

@st.cache_data(ttl=300)
def get_feature_importance(model_id):
    """Get feature importance."""
    try:
        model_manager = get_model_manager()
        return model_manager.get_feature_importance(model_id)
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        return None

@st.cache_data(ttl=300)
def get_recent_predictions(model_id):
    """Get recent predictions."""
    try:
        model_manager = get_model_manager()
        return model_manager.get_recent_predictions(model_id)
    except Exception as e:
        logger.error(f"Error getting recent predictions: {e}")
        return None

@st.cache_data(ttl=300)
def get_model_comparison(model_ids):
    """Get model comparison metrics."""
    try:
        model_manager = get_model_manager()
        return model_manager.compare_models(model_ids)
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        return None

def show():
    """Display the ML Models page."""
    st.title("ML Models")
    
    try:
        # Get model manager
        model_manager = get_model_manager()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Model Management", "Performance Analysis", "Feature Analysis", "Real-time Monitoring"])
        
        with tab1:
            # Model management
            st.subheader("Model Management")
            
            # Create new model
            with st.expander("Create New Model"):
                col1, col2 = st.columns(2)
                
                with col1:
                    model_name = st.text_input("Model Name")
                    description = st.text_area("Description")
                    
                with col2:
                    model_type = st.selectbox(
                        "Model Type",
                        ["Classification", "Regression", "Reinforcement Learning"]
                    )
                    strategy_type = st.selectbox(
                        "Strategy Type",
                        ["Mean Reversion", "Trend Following", "Breakout"]
                    )
                
                # Model architecture
                st.write("### Model Architecture")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    architecture = {}
                    architecture['layers'] = st.multiselect(
                        "Layer Types",
                        ["Dense", "LSTM", "GRU", "Conv1D", "Dropout"],
                        default=["Dense"]
                    )
                    
                    architecture['units'] = st.number_input(
                        "Units per Layer",
                        min_value=8,
                        max_value=512,
                        value=64,
                        step=8
                    )
                    
                with col2:
                    architecture['activation'] = st.selectbox(
                        "Activation Function",
                        ["relu", "tanh", "sigmoid", "softmax"]
                    )
                    
                    architecture['optimizer'] = st.selectbox(
                        "Optimizer",
                        ["adam", "sgd", "rmsprop", "adagrad"]
                    )
                
                # Training settings
                st.write("### Training Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    training_params = {}
                    training_params['batch_size'] = st.number_input(
                        "Batch Size",
                        min_value=16,
                        max_value=256,
                        value=32,
                        step=16
                    )
                    
                    training_params['epochs'] = st.number_input(
                        "Epochs",
                        min_value=10,
                        max_value=1000,
                        value=100,
                        step=10
                    )
                    
                with col2:
                    training_params['learning_rate'] = st.number_input(
                        "Learning Rate",
                        min_value=0.0001,
                        max_value=0.1,
                        value=0.001,
                        step=0.0001
                    )
                    
                    training_params['validation_split'] = st.number_input(
                        "Validation Split",
                        min_value=0.1,
                        max_value=0.3,
                        value=0.2,
                        step=0.05
                    )
                
                # Advanced settings
                with st.expander("Advanced Settings"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        training_params['early_stopping'] = st.checkbox("Enable Early Stopping", value=True)
                        if training_params['early_stopping']:
                            training_params['patience'] = st.number_input(
                                "Early Stopping Patience",
                                min_value=5,
                                max_value=50,
                                value=10,
                                step=5
                            )
                        
                        training_params['class_weight'] = st.selectbox(
                            "Class Weight",
                            ["balanced", "balanced_subsample", "None"]
                        )
                        
                    with col2:
                        training_params['cross_validation'] = st.checkbox("Enable Cross Validation", value=False)
                        if training_params['cross_validation']:
                            training_params['cv_folds'] = st.number_input(
                                "Cross Validation Folds",
                                min_value=2,
                                max_value=10,
                                value=5,
                                step=1
                            )
                        
                        training_params['random_state'] = st.number_input(
                            "Random State",
                            min_value=0,
                            max_value=1000,
                            value=42,
                            step=1
                        )
                
                if st.button("Create Model", type="primary"):
                    try:
                        model_id = model_manager.create_model(
                            name=model_name,
                            description=description,
                            model_type=model_type,
                            strategy_type=strategy_type,
                            architecture=architecture,
                            training_params=training_params
                        )
                        st.success(f"Model created successfully! ID: {model_id}")
                    except Exception as e:
                        logger.error(f"Error creating model: {e}")
                        st.error(f"An error occurred while creating the model: {str(e)}")
            
            # List models
            st.write("### Models")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Status Filter",
                    ["All", "Active", "Inactive", "Training", "Failed"],
                    index=0
                )
            
            with col2:
                type_filter = st.selectbox(
                    "Model Type Filter",
                    ["All", "Classification", "Regression", "Reinforcement Learning"],
                    index=0
                )
            
            with col3:
                date_filter = st.date_input(
                    "Date Range",
                    value=(datetime.now() - timedelta(days=30), datetime.now())
                )
            
            models = get_models()
            if models is None:
                st.error("Failed to load models")
                return
            
            # Filter models
            filtered_models = models
            if status_filter != "All":
                filtered_models = [model for model in filtered_models if model['status'] == status_filter.lower()]
            if type_filter != "All":
                filtered_models = [model for model in filtered_models if model['model_type'] == type_filter]
            filtered_models = [
                model for model in filtered_models 
                if datetime.strptime(model['created_at'], '%Y-%m-%d %H:%M:%S').date() >= date_filter[0]
                and datetime.strptime(model['created_at'], '%Y-%m-%d %H:%M:%S').date() <= date_filter[1]
            ]
            
            for model in filtered_models:
                with st.expander(f"{model['name']} - {model['status']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Description:**")
                        st.write(model['description'])
                        
                    with col2:
                        st.write("**Architecture:**")
                        for param, value in model['architecture'].items():
                            st.write(f"- {param}: {value}")
                            
                    with col3:
                        st.write("**Status:**")
                        st.write(f"- Created: {model['created_at']}")
                        st.write(f"- Status: {model['status']}")
                        st.write(f"- Type: {model['model_type']}")
                    
                    # Model controls
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if model['status'] == 'training':
                            if st.button("Stop", key=f"stop_{model['id']}"):
                                try:
                                    model_manager.stop_training(model['id'])
                                    st.success("Training stopped successfully!")
                                except Exception as e:
                                    logger.error(f"Error stopping training: {e}")
                                    st.error(f"An error occurred while stopping training: {str(e)}")
                        else:
                            if st.button("Train", key=f"train_{model['id']}"):
                                try:
                                    model_manager.train_model(model['id'])
                                    st.success("Training started successfully!")
                                except Exception as e:
                                    logger.error(f"Error starting training: {e}")
                                    st.error(f"An error occurred while starting training: {str(e)}")
                    
                    with col2:
                        if st.button("View Results", key=f"results_{model['id']}"):
                            st.session_state['selected_model'] = model['id']
                            st.experimental_rerun()
                    
                    with col3:
                        if st.button("Export", key=f"export_{model['id']}"):
                            try:
                                metrics = get_model_metrics(model['id'])
                                if metrics:
                                    df = pd.DataFrame(metrics)
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        "Download Metrics",
                                        csv,
                                        f"model_{model['id']}_metrics.csv",
                                        "text/csv"
                                    )
                            except Exception as e:
                                logger.error(f"Error exporting metrics: {e}")
                                st.error(f"An error occurred while exporting metrics: {str(e)}")
                    
                    with col4:
                        if st.button("Delete", key=f"delete_{model['id']}"):
                            try:
                                if model_manager.delete_model(model['id']):
                                    st.success("Model deleted successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete model")
                            except Exception as e:
                                logger.error(f"Error deleting model: {e}")
                                st.error(f"An error occurred while deleting the model: {str(e)}")
        
        with tab2:
            # Performance analysis
            st.subheader("Performance Analysis")
            
            # Get selected model
            selected_model = st.session_state.get('selected_model')
            if not selected_model:
                st.info("Select a model to view its performance analysis")
                return
            
            metrics = get_model_metrics(selected_model)
            if metrics is None:
                st.error("Failed to load model metrics")
                return
            
            # Convert metrics to DataFrame
            df_metrics = pd.DataFrame(metrics)
            
            # Performance metrics
            st.write("### Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Accuracy", f"{df_metrics['accuracy'].iloc[-1]:.2%}")
                st.metric("Precision", f"{df_metrics['precision'].iloc[-1]:.2%}")
                
            with col2:
                st.metric("Recall", f"{df_metrics['recall'].iloc[-1]:.2%}")
                st.metric("F1 Score", f"{df_metrics['f1'].iloc[-1]:.2%}")
                
            with col3:
                st.metric("AUC", f"{df_metrics['auc'].iloc[-1]:.2%}")
                st.metric("Training Time", f"{df_metrics['training_time'].iloc[-1]:.1f}s")
                
            with col4:
                st.metric("Last Updated", df_metrics['timestamp'].iloc[-1])
                st.metric("Total Updates", len(df_metrics))
            
            # Performance visualizations
            st.write("### Performance Visualizations")
            
            # Learning curves
            fig_learning = go.Figure()
            
            fig_learning.add_trace(go.Scatter(
                x=df_metrics['epoch'],
                y=df_metrics['accuracy'],
                mode='lines',
                name='Accuracy'
            ))
            
            fig_learning.add_trace(go.Scatter(
                x=df_metrics['epoch'],
                y=df_metrics['val_accuracy'],
                mode='lines',
                name='Validation Accuracy'
            ))
            
            fig_learning.update_layout(
                title='Learning Curves',
                xaxis_title='Epoch',
                yaxis_title='Accuracy',
                height=400
            )
            
            st.plotly_chart(fig_learning, use_container_width=True)
            
            # Confusion matrix
            if 'confusion_matrix' in df_metrics.columns:
                fig_cm = px.imshow(
                    df_metrics['confusion_matrix'].iloc[-1],
                    title='Confusion Matrix',
                    labels=dict(x="Predicted", y="Actual", color="Count")
                )
                
                st.plotly_chart(fig_cm, use_container_width=True)
            
            # Additional performance metrics
            st.write("### Additional Metrics")
            
            # ROC curve
            fig_roc = go.Figure()
            
            fig_roc.add_trace(go.Scatter(
                x=df_metrics['fpr'].iloc[-1],
                y=df_metrics['tpr'].iloc[-1],
                mode='lines',
                name='ROC Curve'
            ))
            
            fig_roc.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='Random',
                line=dict(dash='dash')
            ))
            
            fig_roc.update_layout(
                title='ROC Curve',
                xaxis_title='False Positive Rate',
                yaxis_title='True Positive Rate',
                height=400
            )
            
            st.plotly_chart(fig_roc, use_container_width=True)
            
            # Training time distribution
            fig_time = px.histogram(
                df_metrics,
                x='training_time',
                title='Training Time Distribution',
                labels=dict(x='Training Time (s)', y='Count')
            )
            
            st.plotly_chart(fig_time, use_container_width=True)
        
        with tab3:
            # Feature analysis
            st.subheader("Feature Analysis")
            
            if not selected_model:
                st.info("Select a model to view feature analysis")
                return
            
            # Get feature importance
            feature_importance = get_feature_importance(selected_model)
            if feature_importance is None:
                st.error("Failed to load feature importance")
                return
            
            # Feature importance visualization
            st.write("### Feature Importance")
            
            fig_importance = px.bar(
                x=list(feature_importance.keys()),
                y=list(feature_importance.values()),
                title='Feature Importance'
            )
            
            st.plotly_chart(fig_importance, use_container_width=True)
            
            # Feature correlation
            st.write("### Feature Correlation")
            
            feature_correlation = model_manager.get_feature_correlation(selected_model)
            if feature_correlation is not None:
                fig_corr = px.imshow(
                    feature_correlation,
                    title='Feature Correlation Heatmap',
                    labels=dict(x="Feature", y="Feature", color="Correlation")
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
            
            # Feature distribution
            st.write("### Feature Distribution")
            
            feature_distribution = model_manager.get_feature_distribution(selected_model)
            if feature_distribution:
                for feature, values in feature_distribution.items():
                    fig_dist = px.histogram(
                        x=values,
                        title=f'{feature} Distribution',
                        labels=dict(x=feature, y="Count")
                    )
                    
                    st.plotly_chart(fig_dist, use_container_width=True)
            
            # Export feature analysis
            if st.button("Export Feature Analysis"):
                try:
                    analysis_results = {
                        'feature_importance': feature_importance,
                        'feature_correlation': feature_correlation.tolist() if feature_correlation is not None else None,
                        'feature_distribution': feature_distribution
                    }
                    
                    json_results = pd.DataFrame(analysis_results).to_json()
                    st.download_button(
                        "Download Feature Analysis",
                        json_results,
                        f"model_{selected_model}_feature_analysis.json",
                        "application/json"
                    )
                except Exception as e:
                    logger.error(f"Error exporting feature analysis: {e}")
                    st.error(f"An error occurred while exporting feature analysis: {str(e)}")
        
        with tab4:
            # Real-time monitoring
            st.subheader("Real-time Monitoring")
            
            if not selected_model:
                st.info("Select a model to view real-time monitoring")
                return
            
            # Get current model status
            model = next((m for m in models if m['id'] == selected_model), None)
            if not model:
                st.error("Model not found")
                return
            
            if model['status'] != 'active':
                st.warning("Model is not currently active")
                return
            
            # Real-time metrics
            st.write("### Current Performance")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Accuracy",
                    f"{df_metrics['accuracy'].iloc[-1]:.2%}"
                )
                
            with col2:
                st.metric(
                    "Predictions Made",
                    f"{len(get_recent_predictions(selected_model))}"
                )
                
            with col3:
                st.metric(
                    "Last Update",
                    f"{datetime.now() - datetime.strptime(df_metrics['timestamp'].iloc[-1], '%Y-%m-%d %H:%M:%S'):.1f}m ago"
                )
            
            # Real-time predictions
            st.write("### Recent Predictions")
            
            predictions = get_recent_predictions(selected_model)
            if predictions:
                df_predictions = pd.DataFrame(predictions)
                
                # Prediction accuracy over time
                fig_pred = go.Figure()
                
                fig_pred.add_trace(go.Scatter(
                    x=df_predictions['timestamp'],
                    y=df_predictions['accuracy'],
                    mode='lines',
                    name='Prediction Accuracy'
                ))
                
                fig_pred.update_layout(
                    title='Prediction Accuracy Over Time',
                    xaxis_title='Time',
                    yaxis_title='Accuracy',
                    height=400
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # Confidence distribution
                fig_conf = px.histogram(
                    df_predictions,
                    x='confidence',
                    title='Prediction Confidence Distribution',
                    labels=dict(x='Confidence', y='Count')
                )
                
                st.plotly_chart(fig_conf, use_container_width=True)
            
            # Auto-refresh
            st.write("### Auto-refresh Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
                
            with col2:
                if auto_refresh:
                    refresh_interval = st.number_input(
                        "Refresh Interval (seconds)",
                        min_value=5,
                        max_value=60,
                        value=10,
                        step=5
                    )
            
            if auto_refresh:
                st.write(f"Next refresh in {refresh_interval} seconds...")
                time.sleep(refresh_interval)
                st.experimental_rerun()
        
    except Exception as e:
        logger.error(f"Error displaying ML Models page: {e}")
        st.error(f"An error occurred while loading the ML Models page: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 