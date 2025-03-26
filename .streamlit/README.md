# Streamlit Deployment Guide

This guide provides instructions for deploying the Crypto Trading Bot to Streamlit Cloud.

## Prerequisites

1. A GitHub account
2. A Streamlit Cloud account
3. The Crypto Trading Bot repository

## Deployment Steps

1. **Prepare Your Repository**
   - Ensure all files are committed to your GitHub repository
   - Make sure your `.gitignore` file is properly configured
   - Verify that all dependencies are listed in `requirements.txt`

2. **Configure Streamlit Cloud**
   - Log in to [Streamlit Cloud](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository
   - Choose the main branch
   - Set the main file path to `run_streamlit.py`

3. **Set Up Secrets**
   - In Streamlit Cloud, go to your app's settings
   - Navigate to the "Secrets" section
   - Add the following secrets:
     ```toml
     [BINANCE]
     api_key = "your_binance_api_key"
     api_secret = "your_binance_api_secret"

     [DATABASE]
     host = "your_database_host"
     port = "your_database_port"
     database = "your_database_name"
     user = "your_database_user"
     password = "your_database_password"

     [MLFLOW]
     tracking_uri = "your_mlflow_tracking_uri"
     ```

4. **Deploy Your App**
   - Click "Deploy" in Streamlit Cloud
   - Wait for the deployment to complete
   - Your app will be available at `https://share.streamlit.io/your-username/your-repo/main/run_streamlit.py`

## Troubleshooting

1. **Deployment Fails**
   - Check the deployment logs for error messages
   - Verify all dependencies are correctly listed in `requirements.txt`
   - Ensure all required files are present in the repository

2. **App Crashes**
   - Check the app logs in Streamlit Cloud
   - Verify all secrets are correctly configured
   - Ensure all API keys and credentials are valid

3. **Performance Issues**
   - Monitor resource usage in Streamlit Cloud
   - Optimize data loading and processing
   - Consider caching frequently accessed data

## Maintenance

1. **Updates**
   - Push changes to your GitHub repository
   - Streamlit Cloud will automatically redeploy

2. **Monitoring**
   - Use Streamlit Cloud's analytics to monitor app usage
   - Set up alerts for errors and performance issues

3. **Backup**
   - Regularly backup your configuration and data
   - Keep a local copy of your secrets

## Security Considerations

1. **API Keys**
   - Never commit API keys to the repository
   - Use Streamlit Cloud's secrets management
   - Rotate keys regularly

2. **Data Protection**
   - Implement proper authentication
   - Use HTTPS for all connections
   - Follow security best practices

## Support

For additional support:
- Check the [Streamlit documentation](https://docs.streamlit.io/)
- Visit the [Streamlit community forum](https://discuss.streamlit.io/)
- Contact the development team 