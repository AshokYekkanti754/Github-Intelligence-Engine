import csv
import json
import io
from typing import List, Dict, Any
from datetime import datetime
from fastapi.responses import StreamingResponse, Response

class ExportService:
    """Handle data export in various formats"""
    
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str = None) -> StreamingResponse:
        """Export data as CSV file"""
        if not data:
            data = [{"message": "No data available"}]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        # Prepare response
        output.seek(0)
        filename = filename or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    @staticmethod
    def export_to_json(data: Any, filename: str = None) -> Response:
        """Export data as JSON file"""
        filename = filename or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return Response(
            content=json.dumps(data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    @staticmethod
    def export_analysis_result(analysis_data: Dict, format: str = "json"):
        """Export single analysis result"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "analysis": analysis_data
        }
        
        if format == "csv":
            # Flatten nested data for CSV
            flat_data = [{
                "username": analysis_data.get("username"),
                "name": analysis_data.get("name"),
                "portfolio_score": analysis_data.get("portfolio_score"),
                "total_repos": analysis_data.get("total_repos"),
                "public_repos": analysis_data.get("public_repos"),
                "private_repos": analysis_data.get("private_repos"),
                "total_stars": analysis_data.get("total_stars"),
                "followers": analysis_data.get("followers"),
                "following": analysis_data.get("following"),
                "top_languages": ", ".join(analysis_data.get("top_languages", [])),
                "skill_level": analysis_data.get("ai_insights", {}).get("skill_level"),
                "summary": analysis_data.get("ai_insights", {}).get("summary")
            }]
            return ExportService.export_to_csv(flat_data, f"{analysis_data['username']}_analysis.csv")
        else:
            return ExportService.export_to_json(export_data, f"{analysis_data['username']}_analysis.json")
    
    @staticmethod
    def export_user_history(history_data: List[Dict], format: str = "json"):
        """Export user's analysis history"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_analyses": len(history_data),
            "history": history_data
        }
        
        if format == "csv":
            # Flatten for CSV
            flat_data = []
            for item in history_data:
                flat_data.append({
                    "analyzed_at": item.get("analyzed_at"),
                    "username": item.get("analyzed_username"),
                    "portfolio_score": item.get("portfolio_score"),
                    "total_repos": item.get("total_repos"),
                    "total_stars": item.get("total_stars"),
                    "top_languages": ", ".join(item.get("top_languages", []))
                })
            return ExportService.export_to_csv(flat_data, f"my_history_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            return ExportService.export_to_json(export_data, f"history_{datetime.now().strftime('%Y%m%d')}.json")
    
    @staticmethod
    def export_saved_profiles(profiles_data: List[Dict], format: str = "json"):
        """Export saved profiles list"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_saved": len(profiles_data),
            "profiles": profiles_data
        }
        
        filename = f"saved_profiles_{datetime.now().strftime('%Y%m%d')}.{format}"
        if format == "csv":
            return ExportService.export_to_csv(profiles_data, filename)
        else:
            return ExportService.export_to_json(export_data, filename)

export_service = ExportService()