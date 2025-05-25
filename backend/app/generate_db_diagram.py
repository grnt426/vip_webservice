import os
import logging

# Configure logging for the script itself
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Attempting to import SQLAlchemy Base, engine, models, and sqlalchemy_schemadisplay...")
        from app.database import Base, engine # Your SQLAlchemy Base and engine
        from app.models import __all__ as all_models # Ensure all models are loaded via __init__.py
        from sqlalchemy_schemadisplay import create_schema_graph

        logger.info(f"Successfully imported modules. SQLAlchemy metadata tables: {list(Base.metadata.tables.keys())}")

        output_dir = "/app/data"
        os.makedirs(output_dir, exist_ok=True)
        output_file_png = os.path.join(output_dir, "db_model_schemadisplay.png")
        output_file_pdf = os.path.join(output_dir, "db_model_schemadisplay.pdf")

        logger.info("Creating schema graph...")
        graph = create_schema_graph(
            engine=engine, # Pass the engine
            metadata=Base.metadata,
            show_datatypes=True,  # Show data types in the diagram
            show_indexes=True,    # Show indexes
            rankdir='LR',         # Left to Right (alternative: 'TB' for Top to Bottom)
            concentrate=False     # Avoids edge merging for clarity
        )

        logger.info(f"Generating ER diagram (PNG) to {output_file_png}...")
        graph.write_png(output_file_png)
        logger.info(f"ER diagram (PNG) generated successfully: {output_file_png}")

        logger.info(f"Generating ER diagram (PDF) to {output_file_pdf}...")
        graph.write_pdf(output_file_pdf)
        logger.info(f"ER diagram (PDF) generated successfully: {output_file_pdf}")

    except ImportError as ie:
        logger.error(f"ImportError: Could not import necessary modules. {ie}", exc_info=True)
    except Exception as e:
        # Catch if graphviz (dot command) is not found or other errors
        if "dot" in str(e).lower() and "not found" in str(e).lower():
            logger.error(f"Graphviz 'dot' command not found. Ensure Graphviz is installed in the Docker container and in PATH. {e}", exc_info=True)
        else:
            logger.error(f"An error occurred during diagram generation: {e}", exc_info=True) 