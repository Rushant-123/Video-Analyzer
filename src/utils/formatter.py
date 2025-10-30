"""Output formatting utilities"""

import json
from typing import List, Dict


class OutputFormatter:
    """Formats analysis results for console output"""
    
    @staticmethod
    def format_results(analyses: List[Dict]) -> None:
        """Print formatted analysis results to console
        
        Args:
            analyses: List of analysis dictionaries
        """
        print("\n" + "="*50)
        print("VIDEO REASONING RESULTS")
        print("="*50 + "\n")
        
        for i, analysis in enumerate(analyses, 1):
            print(f"🔍 Clip {i}: {analysis['clip_start']:.1f}s - {analysis['clip_end']:.1f}s")
            print(f"📝 Summary: {analysis['summary']}")
            
            promises = analysis.get('promises', [])
            print(f"🤝 Promises: {', '.join(promises) if promises else 'None'}")
            
            print(f"🫴 Body Language: {analysis.get('body_language', 'N/A')}")
            print(f"🎯 Confidence: {analysis.get('confidence_score', 0.0):.2f}")
            
            actions = analysis.get('actions', [])
            print(f"⚡ Actions: {', '.join(actions) if actions else 'None'}")
            print()
        
        print("="*50)
        print("FULL RESULTS (JSON):")
        print("="*50)
        print(json.dumps(analyses, indent=2))

