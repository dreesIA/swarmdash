"""Data loading and caching functions"""
import streamlit as st
import pandas as pd
import os
import concurrent.futures
from typing import Dict, List, Optional

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(path: str) -> pd.DataFrame:
    """Load and preprocess CSV data with caching"""
    try:
        if not os.path.exists(path):
            st.error(f"File not found: {path}")
            return pd.DataFrame()
            
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        df.dropna(subset=["Player Name"], inplace=True)
        df["Session Type"] = df["Session Type"].astype(str).str.strip().str.title()
        
        # Convert metrics to numeric
        from core.constants import METRICS
        for col in METRICS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Add timestamp if not present
        if 'timestamp' not in df.columns and 'date' not in df.columns:
            df['timestamp'] = pd.to_datetime(df.index, errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading {path}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_multiple_files(file_dict: Dict[str, str]) -> pd.DataFrame:
    """Load multiple files and concatenate them"""
    all_data = []
    for name, path in file_dict.items():
        df = load_data(path)
        if not df.empty:
            df['Source'] = name
            all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

@st.cache_data(ttl=3600)
def load_multiple_files_parallel(file_dict: Dict[str, str], max_workers: int = 4) -> Dict[str, pd.DataFrame]:
    """Load multiple files in parallel for better performance"""
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {executor.submit(load_data, path): name 
                         for name, path in file_dict.items()}
        
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as e:
                st.error(f"Error loading {name}: {str(e)}")
                results[name] = pd.DataFrame()
    
    return results

@st.cache_data(ttl=3600)
def load_event_data(file_path: str) -> pd.DataFrame:
    """Load event data from Excel file"""
    try:
        xls = pd.ExcelFile(file_path)
        df = xls.parse("Nacsport")
        return df
    except Exception as e:
        st.error(f"Error loading event data: {str(e)}")
        return pd.DataFrame()
