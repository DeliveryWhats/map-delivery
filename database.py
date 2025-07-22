from typing import List, Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import config

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(config.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_active_regions(self, company_id: str, store_id: Optional[str] = None) -> List[Dict]:
        """Get active regions for a company, optionally filtered by store_id"""
        with self.engine.connect() as conn:
            if store_id:
                result = conn.execute(text('''
                    SELECT id, company_id, store_id, type, region_name, file_path
                    FROM company_delivery_map 
                    WHERE company_id = :company_id AND store_id = :store_id AND status = 1
                '''), {"company_id": company_id, "store_id": store_id})
            else:
                result = conn.execute(text('''
                    SELECT id, company_id, store_id, type, region_name, file_path
                    FROM company_delivery_map 
                    WHERE company_id = :company_id AND status = 1
                    ORDER BY id ASC
                '''), {"company_id": company_id})
            
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in result.fetchall()]
            return results
    

