from sqlalchemy.orm import Session
from config.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError

class BaseDAO:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def commit(self):
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def refresh(self, instance):
        self.db.refresh(instance)
    
    def close(self):
        self.db.close()
        
    def insert(self, instance):
        self.db.add(instance)
        self.commit()
        
    def bulk_insert(self, instances):
        self.db.add_all(instances)
        self.commit()

    def query(self, model):
        return self.db.query(model)
        
    def update(self, model, filter_conditions, update_values):
        self.db.query(model).filter(*filter_conditions).update(update_values)
        self.commit()