import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from app.ml.experiment_manager import ExperimentManager
from app.ml.model_manager import ModelManager
from app.trading.exchange_client import ExchangeClient
import time

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def get_experiment_manager():
    """Get experiment manager instance."""
    return ExperimentManager()

@st.cache_resource(ttl=300)
def get_model_manager():
    """Get model manager instance."""
    return ModelManager()

@st.cache_resource(ttl=300)
def get_exchange_client():
    """Get exchange client instance."""
    return ExchangeClient()

@st.cache_data(ttl=300)
def get_experiments():
    """Get list of experiments."""
    try:
        experiment_manager = get_experiment_manager()
        return experiment_manager.get_experiments()
    except Exception as e:
        logger.error(f"Error getting experiments: {e}")
        return None

@st.cache_data(ttl=300)
def get_experiment_results(experiment_id):
    """Get experiment results."""
    try:
        experiment_manager = get_experiment_manager()
        return experiment_manager.get_experiment_results(experiment_id)
    except Exception as e:
        logger.error(f"Error getting experiment results: {e}")
        return None

@st.cache_data(ttl=300)
def get_parameter_combinations(experiment_id):
    """Get parameter combinations for an experiment."""
    try:
        experiment_manager = get_experiment_manager()
        return experiment_manager.get_parameter_combinations(experiment_id)
    except Exception as e:
        logger.error(f"Error getting parameter combinations: {e}")
        return None

@st.cache_data(ttl=60)
def get_experiment_templates():
    """Get available experiment templates."""
    try:
        experiment_manager = get_experiment_manager()
        return experiment_manager.get_experiment_templates()
    except Exception as e:
        logger.error(f"Error getting experiment templates: {e}")
        return None

def show():
    """Display the Experiment Tracking page."""
    st.title("Experiment Tracking")
    
    try:
        # Get experiment manager
        experiment_manager = get_experiment_manager()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Experiments", "Performance Analysis", "Parameter Optimization", "Real-time Monitoring"])
        
        with tab1:
            # Experiment management
            st.subheader("Experiment Management")
            
            # Create new experiment
            with st.expander("Create New Experiment"):
                # Template selection
                templates = get_experiment_templates()
                if templates:
                    template = st.selectbox(
                        "Select Template",
                        ["Custom"] + list(templates.keys()),
                        index=0
                    )
                    
                    if template != "Custom":
                        template_config = templates[template]
                        experiment_name = st.text_input("Experiment Name", value=f"{template}_experiment")
                        description = st.text_area("Description", value=template_config.get('description', ''))
                        model_type = st.selectbox("Model Type", [template_config['model_type']])
                        strategy_type = st.selectbox("Strategy Type", [template_config['strategy_type']])
                        param_ranges = template_config['param_ranges']
                        training_params = template_config['training_params']
                    else:
                        # Original custom experiment creation form
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            experiment_name = st.text_input("Experiment Name")
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
                        
                        # Parameter ranges
                        st.write("### Parameter Ranges")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            param_ranges = {}
                            param_ranges['learning_rate'] = st.slider(
                                "Learning Rate",
                                min_value=0.0001,
                                max_value=0.1,
                                value=(0.001, 0.01),
                                step=0.0001
                            )
                            
                            param_ranges['batch_size'] = st.slider(
                                "Batch Size",
                                min_value=16,
                                max_value=256,
                                value=(32, 128),
                                step=16
                            )
                            
                        with col2:
                            param_ranges['epochs'] = st.slider(
                                "Epochs",
                                min_value=10,
                                max_value=1000,
                                value=(50, 200),
                                step=10
                            )
                            
                            param_ranges['dropout_rate'] = st.slider(
                                "Dropout Rate",
                                min_value=0.0,
                                max_value=0.5,
                                value=(0.1, 0.3),
                                step=0.05
                            )
                        
                        # Training settings
                        st.write("### Training Settings")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            training_params = {}
                            training_params['validation_split'] = st.number_input(
                                "Validation Split",
                                min_value=0.1,
                                max_value=0.3,
                                value=0.2,
                                step=0.05
                            )
                            
                            training_params['early_stopping_patience'] = st.number_input(
                                "Early Stopping Patience",
                                min_value=5,
                                max_value=50,
                                value=10,
                                step=5
                            )
                            
                        with col2:
                            training_params['max_trials'] = st.number_input(
                                "Max Trials",
                                min_value=10,
                                max_value=1000,
                                value=100,
                                step=10
                            )
                            
                            training_params['optimization_metric'] = st.selectbox(
                                "Optimization Metric",
                                ["accuracy", "precision", "recall", "f1", "auc"]
                            )
                
                # Advanced settings
                with st.expander("Advanced Settings"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        training_params['cross_validation'] = st.number_input(
                            "Cross Validation Folds",
                            min_value=2,
                            max_value=10,
                            value=5,
                            step=1
                        )
                        
                        training_params['class_weight'] = st.selectbox(
                            "Class Weight",
                            ["balanced", "balanced_subsample", "None"]
                        )
                        
                    with col2:
                        training_params['random_state'] = st.number_input(
                            "Random State",
                            min_value=0,
                            max_value=1000,
                            value=42,
                            step=1
                        )
                        
                        training_params['n_jobs'] = st.number_input(
                            "Number of Jobs",
                            min_value=1,
                            max_value=8,
                            value=4,
                            step=1
                        )
                
                # Save as template
                save_as_template = st.checkbox("Save as Template")
                if save_as_template:
                    template_name = st.text_input("Template Name")
                
                if st.button("Create Experiment", type="primary"):
                    try:
                        experiment_id = experiment_manager.create_experiment(
                            name=experiment_name,
                            description=description,
                            model_type=model_type,
                            strategy_type=strategy_type,
                            param_ranges=param_ranges,
                            training_params=training_params
                        )
                        
                        if save_as_template and template_name:
                            experiment_manager.save_experiment_template(
                                template_name,
                                {
                                    'description': description,
                                    'model_type': model_type,
                                    'strategy_type': strategy_type,
                                    'param_ranges': param_ranges,
                                    'training_params': training_params
                                }
                            )
                        
                        st.success(f"Experiment created successfully! ID: {experiment_id}")
                    except Exception as e:
                        logger.error(f"Error creating experiment: {e}")
                        st.error(f"An error occurred while creating the experiment: {str(e)}")
            
            # List experiments
            st.write("### Experiments")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Status Filter",
                    ["All", "Running", "Completed", "Failed", "Stopped"],
                    index=0
                )
            
            with col2:
                model_filter = st.selectbox(
                    "Model Type Filter",
                    ["All", "Classification", "Regression", "Reinforcement Learning"],
                    index=0
                )
            
            with col3:
                date_filter = st.date_input(
                    "Date Range",
                    value=(datetime.now() - timedelta(days=30), datetime.now())
                )
            
            experiments = get_experiments()
            if experiments is None:
                st.error("Failed to load experiments")
                return
            
            # Filter experiments
            filtered_experiments = experiments
            if status_filter != "All":
                filtered_experiments = [exp for exp in filtered_experiments if exp['status'] == status_filter.lower()]
            if model_filter != "All":
                filtered_experiments = [exp for exp in filtered_experiments if exp['model_type'] == model_filter]
            filtered_experiments = [
                exp for exp in filtered_experiments 
                if datetime.strptime(exp['created_at'], '%Y-%m-%d %H:%M:%S').date() >= date_filter[0]
                and datetime.strptime(exp['created_at'], '%Y-%m-%d %H:%M:%S').date() <= date_filter[1]
            ]
            
            for exp in filtered_experiments:
                with st.expander(f"{exp['name']} - {exp['status']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Description:**")
                        st.write(exp['description'])
                        
                    with col2:
                        st.write("**Parameters:**")
                        for param, value in exp['param_ranges'].items():
                            st.write(f"- {param}: {value}")
                            
                    with col3:
                        st.write("**Status:**")
                        st.write(f"- Created: {exp['created_at']}")
                        st.write(f"- Status: {exp['status']}")
                        st.write(f"- Trials: {exp['trials_completed']}/{exp['max_trials']}")
                    
                    # Experiment controls
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if exp['status'] == 'running':
                            if st.button("Stop", key=f"stop_{exp['id']}"):
                                try:
                                    experiment_manager.stop_experiment(exp['id'])
                                    st.success("Experiment stopped successfully!")
                                except Exception as e:
                                    logger.error(f"Error stopping experiment: {e}")
                                    st.error(f"An error occurred while stopping the experiment: {str(e)}")
                        else:
                            if st.button("Start", key=f"start_{exp['id']}"):
                                try:
                                    experiment_manager.start_experiment(exp['id'])
                                    st.success("Experiment started successfully!")
                                except Exception as e:
                                    logger.error(f"Error starting experiment: {e}")
                                    st.error(f"An error occurred while starting the experiment: {str(e)}")
                    
                    with col2:
                        if st.button("View Results", key=f"results_{exp['id']}"):
                            st.session_state['selected_experiment'] = exp['id']
                            st.experimental_rerun()
                    
                    with col3:
                        if st.button("Export", key=f"export_{exp['id']}"):
                            try:
                                results = get_experiment_results(exp['id'])
                                if results:
                                    df = pd.DataFrame(results)
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        "Download Results",
                                        csv,
                                        f"experiment_{exp['id']}_results.csv",
                                        "text/csv"
                                    )
                            except Exception as e:
                                logger.error(f"Error exporting results: {e}")
                                st.error(f"An error occurred while exporting results: {str(e)}")
                    
                    with col4:
                        if st.button("Delete", key=f"delete_{exp['id']}"):
                            try:
                                if experiment_manager.delete_experiment(exp['id']):
                                    st.success("Experiment deleted successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete experiment")
                            except Exception as e:
                                logger.error(f"Error deleting experiment: {e}")
                                st.error(f"An error occurred while deleting the experiment: {str(e)}")
        
        with tab2:
            # Performance analysis
            st.subheader("Performance Analysis")
            
            # Get selected experiment
            selected_experiment = st.session_state.get('selected_experiment')
            if not selected_experiment:
                st.info("Select an experiment to view its performance analysis")
                return
            
            results = get_experiment_results(selected_experiment)
            if results is None:
                st.error("Failed to load experiment results")
                return
            
            # Convert results to DataFrame
            df_results = pd.DataFrame(results)
            
            # Performance metrics
            st.write("### Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Best Accuracy", f"{df_results['accuracy'].max():.2%}")
                st.metric("Best Precision", f"{df_results['precision'].max():.2%}")
                
            with col2:
                st.metric("Best Recall", f"{df_results['recall'].max():.2%}")
                st.metric("Best F1 Score", f"{df_results['f1'].max():.2%}")
                
            with col3:
                st.metric("Best AUC", f"{df_results['auc'].max():.2%}")
                st.metric("Avg Training Time", f"{df_results['training_time'].mean():.1f}s")
                
            with col4:
                st.metric("Best Trial", f"#{df_results['trial_number'].iloc[df_results['accuracy'].argmax()]}")
                st.metric("Completed Trials", len(df_results))
            
            # Performance visualizations
            st.write("### Performance Visualizations")
            
            # Learning curves
            fig_learning = go.Figure()
            
            for trial in df_results['trial_number'].unique():
                trial_data = df_results[df_results['trial_number'] == trial]
                fig_learning.add_trace(go.Scatter(
                    x=trial_data['epoch'],
                    y=trial_data['accuracy'],
                    mode='lines',
                    name=f'Trial {trial}'
                ))
            
            fig_learning.update_layout(
                title='Learning Curves by Trial',
                xaxis_title='Epoch',
                yaxis_title='Accuracy',
                height=400
            )
            
            st.plotly_chart(fig_learning, use_container_width=True)
            
            # Parameter importance
            param_importance = experiment_manager.get_parameter_importance(selected_experiment)
            if param_importance:
                fig_importance = px.bar(
                    x=list(param_importance.keys()),
                    y=list(param_importance.values()),
                    title='Parameter Importance'
                )
                
                st.plotly_chart(fig_importance, use_container_width=True)
            
            # Confusion matrix
            best_trial = df_results.loc[df_results['accuracy'].idxmax()]
            if 'confusion_matrix' in best_trial:
                fig_cm = px.imshow(
                    best_trial['confusion_matrix'],
                    title='Confusion Matrix (Best Trial)',
                    labels=dict(x="Predicted", y="Actual", color="Count")
                )
                
                st.plotly_chart(fig_cm, use_container_width=True)
            
            # Additional performance metrics
            st.write("### Additional Metrics")
            
            # ROC curves for all trials
            fig_roc = go.Figure()
            
            for trial in df_results['trial_number'].unique():
                trial_data = df_results[df_results['trial_number'] == trial]
                fig_roc.add_trace(go.Scatter(
                    x=trial_data['fpr'],
                    y=trial_data['tpr'],
                    mode='lines',
                    name=f'Trial {trial}'
                ))
            
            fig_roc.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='Random',
                line=dict(dash='dash')
            ))
            
            fig_roc.update_layout(
                title='ROC Curves by Trial',
                xaxis_title='False Positive Rate',
                yaxis_title='True Positive Rate',
                height=400
            )
            
            st.plotly_chart(fig_roc, use_container_width=True)
            
            # Training time distribution
            fig_time = px.histogram(
                df_results,
                x='training_time',
                title='Training Time Distribution',
                labels=dict(x='Training Time (s)', y='Count')
            )
            
            st.plotly_chart(fig_time, use_container_width=True)
        
        with tab3:
            # Parameter optimization
            st.subheader("Parameter Optimization")
            
            if not selected_experiment:
                st.info("Select an experiment to view parameter optimization")
                return
            
            # Get parameter combinations
            param_combinations = get_parameter_combinations(selected_experiment)
            if param_combinations is None:
                st.error("Failed to load parameter combinations")
                return
            
            # Parameter optimization visualization
            st.write("### Parameter Optimization")
            
            # Parameter correlation heatmap
            param_correlation = experiment_manager.get_parameter_correlation(selected_experiment)
            if param_correlation is not None:
                fig_corr = px.imshow(
                    param_correlation,
                    title='Parameter Correlation Heatmap',
                    labels=dict(x="Parameter", y="Parameter", color="Correlation")
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
            
            # Parameter distribution
            param_distribution = experiment_manager.get_parameter_distribution(selected_experiment)
            if param_distribution:
                for param, values in param_distribution.items():
                    fig_dist = px.histogram(
                        x=values,
                        title=f'{param} Distribution',
                        labels=dict(x=param, y="Count")
                    )
                    
                    st.plotly_chart(fig_dist, use_container_width=True)
            
            # Best parameters
            st.write("### Best Parameters")
            
            best_params = experiment_manager.get_best_parameters(selected_experiment)
            if best_params:
                for param, value in best_params.items():
                    st.write(f"- **{param}:** {value}")
            
            # Export optimization results
            if st.button("Export Optimization Results"):
                try:
                    optimization_results = {
                        'best_parameters': best_params,
                        'parameter_importance': param_importance,
                        'parameter_correlation': param_correlation.tolist() if param_correlation is not None else None,
                        'parameter_distribution': param_distribution
                    }
                    
                    json_results = pd.DataFrame(optimization_results).to_json()
                    st.download_button(
                        "Download Optimization Results",
                        json_results,
                        f"experiment_{selected_experiment}_optimization.json",
                        "application/json"
                    )
                except Exception as e:
                    logger.error(f"Error exporting optimization results: {e}")
                    st.error(f"An error occurred while exporting optimization results: {str(e)}")
        
        with tab4:
            # Real-time monitoring
            st.subheader("Real-time Monitoring")
            
            if not selected_experiment:
                st.info("Select an experiment to view real-time monitoring")
                return
            
            # Get current experiment status
            experiment = next((exp for exp in experiments if exp['id'] == selected_experiment), None)
            if not experiment:
                st.error("Experiment not found")
                return
            
            if experiment['status'] != 'running':
                st.warning("Experiment is not currently running")
                return
            
            # Real-time metrics
            st.write("### Current Progress")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Trials Completed",
                    f"{experiment['trials_completed']}/{experiment['max_trials']}",
                    f"{experiment['trials_completed']/experiment['max_trials']*100:.1f}%"
                )
                
            with col2:
                st.metric(
                    "Best Accuracy",
                    f"{df_results['accuracy'].max():.2%}"
                )
                
            with col3:
                st.metric(
                    "Time Elapsed",
                    f"{datetime.now() - datetime.strptime(experiment['created_at'], '%Y-%m-%d %H:%M:%S'):.1f}h"
                )
            
            # Real-time learning curves
            st.write("### Real-time Learning Curves")
            
            fig_rt = go.Figure()
            
            for trial in df_results['trial_number'].unique():
                trial_data = df_results[df_results['trial_number'] == trial]
                fig_rt.add_trace(go.Scatter(
                    x=trial_data['epoch'],
                    y=trial_data['accuracy'],
                    mode='lines',
                    name=f'Trial {trial}'
                ))
            
            fig_rt.update_layout(
                title='Real-time Learning Curves',
                xaxis_title='Epoch',
                yaxis_title='Accuracy',
                height=400
            )
            
            st.plotly_chart(fig_rt, use_container_width=True)
            
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
        logger.error(f"Error displaying Experiment Tracking page: {e}")
        st.error(f"An error occurred while loading the Experiment Tracking page: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 