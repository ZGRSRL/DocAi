"""
Documentation Agent for SAP ME/MII Projects
- Generates Technical Training Materials
- Creates QA Test Scenarios
- Based on development summaries and analysis data
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# Import existing modules
from rag_consultant import ask as rag_ask

class DocumentationAgent:
    """AI-powered documentation generator for SAP ME/MII projects"""
    
    def __init__(self, analysis_dir: Path, model: str = "llama3.1:8b"):
        self.analysis_dir = analysis_dir
        self.model = model
        self.analysis_data = {}
        self.load_analysis_data()
    
    def load_analysis_data(self):
        """Load analysis data from directory"""
        try:
            # Load JSON data
            json_path = self.analysis_dir / 'sapui5_deep_analysis.json'
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.analysis_data = json.load(f)
            
            # Load summary data
            summary_path = self.analysis_dir / 'ADVANCED_SUMMARY.md'
            if summary_path.exists():
                self.summary_text = summary_path.read_text(encoding='utf-8')
            else:
                self.summary_text = "Summary not available"
                
            return True
        except Exception as e:
            print(f"Error loading analysis data: {e}")
            return False
    
    def extract_development_context(self, dev_summary: str) -> Dict[str, Any]:
        """Extract development context from summary"""
        context = {
            'changes': [],
            'affected_controllers': [],
            'affected_services': [],
            'affected_functions': [],
            'risk_areas': []
        }
        
        # Extract controller changes
        controller_patterns = [
            r'(\w+Controller\.js)',
            r'(\w+\.controller\.js)',
            r'(\w+Controller)'
        ]
        
        for pattern in controller_patterns:
            matches = re.findall(pattern, dev_summary, re.IGNORECASE)
            context['affected_controllers'].extend(matches)
        
        # Extract service changes
        service_patterns = [
            r'(\w+Service)',
            r'(\w+Manager)',
            r'(\w+Helper)'
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, dev_summary, re.IGNORECASE)
            context['affected_services'].extend(matches)
        
        # Extract function changes
        function_patterns = [
            r'(\w+\(\))',
            r'(\w+\([^)]*\))',
            r'on(\w+)',
            r'get(\w+)',
            r'set(\w+)'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, dev_summary, re.IGNORECASE)
            context['affected_functions'].extend(matches)
        
        # Identify risk areas
        risk_keywords = ['security', 'authentication', 'authorization', 'websocket', 'api', 'error', 'validation']
        for keyword in risk_keywords:
            if keyword.lower() in dev_summary.lower():
                context['risk_areas'].append(keyword)
        
        return context
    
    def generate_training_material(self, dev_summary: str) -> str:
        """Generate technical training material"""
        
        # Extract development context
        context = self.extract_development_context(dev_summary)
        
        # Get analysis insights
        insights = self.extract_analysis_insights()
        
        # Generate training material using RAG
        training_prompt = f"""
        Generate a comprehensive technical training material for SAP ME/MII project based on the following development summary and analysis data:
        
        DEVELOPMENT SUMMARY:
        {dev_summary}
        
        ANALYSIS INSIGHTS:
        - Controllers: {insights['controllers']}
        - Functions: {insights['functions']}
        - ME APIs: {insights['me_apis']}
        - Error Codes: {insights['error_codes']}
        - BaseController Functions: {insights['basecontroller_functions']}
        
        CONTEXT:
        - Affected Controllers: {', '.join(context['affected_controllers'])}
        - Affected Services: {', '.join(context['affected_services'])}
        - Risk Areas: {', '.join(context['risk_areas'])}
        
        Please generate a structured training material with the following sections:
        
        1. ARCHITECTURAL CHANGES OVERVIEW
        2. CRITICAL SERVICE USAGE GUIDES
        3. ME DOMAIN FUNCTIONS REFERENCE
        4. SECURITY AND BEST PRACTICES
        5. TROUBLESHOOTING GUIDE
        
        Format as Markdown with clear headings, code examples, and practical guidance.
        """
        
        try:
            training_material = rag_ask(training_prompt, output_dir=str(self.analysis_dir))
            return training_material
        except Exception as e:
            return f"Error generating training material: {e}"
    
    def generate_qa_test_scenarios(self, dev_summary: str) -> str:
        """Generate QA test scenarios"""
        
        # Extract development context
        context = self.extract_development_context(dev_summary)
        
        # Get analysis insights
        insights = self.extract_analysis_insights()
        
        # Generate test scenarios using RAG
        qa_prompt = f"""
        Generate comprehensive QA test scenarios for SAP ME/MII project based on the following development summary and analysis data:
        
        DEVELOPMENT SUMMARY:
        {dev_summary}
        
        ANALYSIS INSIGHTS:
        - Controllers: {insights['controllers']}
        - Functions: {insights['functions']}
        - ME APIs: {insights['me_apis']}
        - Error Codes: {insights['error_codes']}
        - Critical Error Codes: {insights['critical_error_codes']}
        
        CONTEXT:
        - Affected Controllers: {', '.join(context['affected_controllers'])}
        - Affected Services: {', '.join(context['affected_services'])}
        - Risk Areas: {', '.join(context['risk_areas'])}
        
        Please generate test scenarios in the following format:
        
        | Test ID | Test Scenario | Focus Area | Related Controller/View | Priority | Expected Result |
        |---------|---------------|------------|------------------------|----------|-----------------|
        | TS_001 | [Detailed test scenario] | [Focus area] | [Controller/View] | High/Medium/Low | [Expected result] |
        
        Include:
        1. Functional test scenarios
        2. Integration test scenarios
        3. Security test scenarios
        4. Performance test scenarios
        5. Error handling test scenarios
        
        Focus on critical business workflows and the changes mentioned in the development summary.
        """
        
        try:
            qa_scenarios = rag_ask(qa_prompt, output_dir=str(self.analysis_dir))
            return qa_scenarios
        except Exception as e:
            return f"Error generating QA scenarios: {e}"
    
    def extract_analysis_insights(self) -> Dict[str, Any]:
        """Extract key insights from analysis data"""
        insights = {
            'controllers': len(self.analysis_data.get('controllers', [])),
            'functions': sum(len(ctrl.get('functions', [])) for ctrl in self.analysis_data.get('controllers', [])),
            'me_apis': len(self.analysis_data.get('sap_me_apis', [])),
            'error_codes': len([k for k in self.analysis_data.get('i18n', {}).keys() if 'error.label' in k]),
            'critical_error_codes': len([k for k in self.analysis_data.get('i18n', {}).keys() if k.startswith('13') and 'error.label' in k]),
            'basecontroller_functions': 0,
            'websocket_usage': False
        }
        
        # BaseController analysis
        for ctrl in self.analysis_data.get('controllers', []):
            if 'BaseController' in ctrl.get('file', ''):
                insights['basecontroller_functions'] = len(ctrl.get('functions', []))
                break
        
        # WebSocket usage
        for ctrl in self.analysis_data.get('controllers', []):
            functions = ctrl.get('functions', [])
            if any('WebSocket' in func for func in functions):
                insights['websocket_usage'] = True
                break
        
        return insights
    
    def generate_complete_documentation(self, dev_summary: str) -> Dict[str, str]:
        """Generate complete documentation package"""
        
        print("🎓 Generating Technical Training Material...")
        training_material = self.generate_training_material(dev_summary)
        
        print("✅ Generating QA Test Scenarios...")
        qa_scenarios = self.generate_qa_test_scenarios(dev_summary)
        
        # Generate summary
        summary = f"""
# Documentation Package Summary

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Development Summary:** {dev_summary[:100]}...
**Analysis Data:** {self.analysis_dir.name}

## Contents
1. Technical Training Material
2. QA Test Scenarios
3. Implementation Guidelines

## Key Metrics
- Controllers Analyzed: {len(self.analysis_data.get('controllers', []))}
- Functions Documented: {sum(len(ctrl.get('functions', [])) for ctrl in self.analysis_data.get('controllers', []))}
- ME APIs Covered: {len(self.analysis_data.get('sap_me_apis', []))}
- Error Scenarios: {len([k for k in self.analysis_data.get('i18n', {}).keys() if 'error.label' in k])}

## Usage
- Use Training Material for developer onboarding
- Use QA Scenarios for testing and validation
- Review Implementation Guidelines for best practices
        """
        
        return {
            'summary': summary,
            'training_material': training_material,
            'qa_scenarios': qa_scenarios,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'dev_summary': dev_summary,
                'analysis_dir': str(self.analysis_dir),
                'model': self.model
            }
        }
    
    def save_documentation(self, documentation: Dict[str, str], output_dir: Path = None):
        """Save documentation to files"""
        if output_dir is None:
            output_dir = self.analysis_dir / 'documentation'
        
        output_dir.mkdir(exist_ok=True)
        
        # Save training material
        training_path = output_dir / 'TRAINING_MATERIAL.md'
        with open(training_path, 'w', encoding='utf-8') as f:
            f.write(documentation['training_material'])
        
        # Save QA scenarios
        qa_path = output_dir / 'QA_TEST_SCENARIOS.md'
        with open(qa_path, 'w', encoding='utf-8') as f:
            f.write(documentation['qa_scenarios'])
        
        # Save summary
        summary_path = output_dir / 'DOCUMENTATION_SUMMARY.md'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(documentation['summary'])
        
        # Save metadata
        metadata_path = output_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(documentation['metadata'], f, indent=2)
        
        print(f"📁 Documentation saved to: {output_dir}")
        print(f"   - Training Material: {training_path}")
        print(f"   - QA Scenarios: {qa_path}")
        print(f"   - Summary: {summary_path}")
        print(f"   - Metadata: {metadata_path}")
        
        return output_dir

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Documentation Agent for SAP ME/MII Projects')
    parser.add_argument('dev_summary', help='Development summary or change log')
    parser.add_argument('--analysis-dir', default='./tvmes_enhanced_analysis', 
                       help='Analysis directory path')
    parser.add_argument('--model', default='llama3.1:8b', 
                       help='Ollama model to use')
    parser.add_argument('--output-dir', help='Output directory for documentation')
    
    args = parser.parse_args()
    
    # Initialize agent
    analysis_dir = Path(args.analysis_dir)
    if not analysis_dir.exists():
        print(f"❌ Analysis directory not found: {analysis_dir}")
        return
    
    agent = DocumentationAgent(analysis_dir, args.model)
    
    print("🤖 Documentation Agent Starting...")
    print(f"📁 Analysis Directory: {analysis_dir}")
    print(f"🧠 Model: {args.model}")
    print(f"📝 Development Summary: {args.dev_summary[:100]}...")
    
    # Generate documentation
    documentation = agent.generate_complete_documentation(args.dev_summary)
    
    # Save documentation
    output_dir = Path(args.output_dir) if args.output_dir else None
    agent.save_documentation(documentation, output_dir)
    
    print("✅ Documentation generation completed!")

if __name__ == "__main__":
    main()

