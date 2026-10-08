from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

class ReportService:
    @staticmethod
    def generate_plant_pdf(plant, readings, diagnoses, predictions):
        """Generate a professionally styled PDF report for a plant's health and growth metrics"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#27ae60'),
            spaceAfter=15,
            alignment=1 # Centered
        )
        
        h2_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6
        )
        
        th_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )
        
        td_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#2c3e50')
        )
        
        story = []
        
        # Title
        story.append(Paragraph("Precision Farming Report", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %I:%M %p')}", ParagraphStyle('Sub', alignment=1, fontSize=9, textColor=colors.gray)))
        story.append(Spacer(1, 15))
        
        # Plant Overview Info Block
        story.append(Paragraph("Plant Profile Overview", h2_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7'), spaceAfter=10))
        
        overview_data = [
            [Paragraph("<b>Plant ID:</b>", body_style), Paragraph(str(plant.id), body_style), 
             Paragraph("<b>Plant Name:</b>", body_style), Paragraph(plant.name, body_style)],
            [Paragraph("<b>Crop Type:</b>", body_style), Paragraph(plant.crop_type, body_style), 
             Paragraph("<b>Age (Days):</b>", body_style), Paragraph(str(plant.current_age), body_style)],
            [Paragraph("<b>Sowing Date:</b>", body_style), Paragraph(plant.sowing_date.strftime('%Y-%m-%d'), body_style), 
             Paragraph("<b>Soil Type:</b>", body_style), Paragraph(plant.soil_type, body_style)],
            [Paragraph("<b>Status:</b>", body_style), Paragraph(plant.status, body_style), 
             Paragraph("<b>Height (cm):</b>", body_style), Paragraph(f"{plant.height_cm:.2f} cm", body_style)]
        ]
        
        t_overview = Table(overview_data, colWidths=[100, 150, 100, 150])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e9ecef')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef'))
        ]))
        story.append(t_overview)
        story.append(Spacer(1, 15))
        
        # Sensor Readings Table
        story.append(Paragraph("Recent Telemetry Data (Last 5 Readings)", h2_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7'), spaceAfter=10))
        
        if readings:
            sensor_headers = [
                Paragraph("Timestamp", th_style), 
                Paragraph("Temp (°C)", th_style), 
                Paragraph("Humidity (%)", th_style), 
                Paragraph("Moisture (%)", th_style), 
                Paragraph("pH", th_style), 
                Paragraph("Light (Lux)", th_style)
            ]
            sensor_table_data = [sensor_headers]
            for r in readings[:5]:
                sensor_table_data.append([
                    Paragraph(r.timestamp.strftime('%Y-%m-%d %H:%M'), td_style),
                    Paragraph(f"{r.temperature:.1f}", td_style),
                    Paragraph(f"{r.humidity:.1f}", td_style),
                    Paragraph(f"{r.soil_moisture:.1f}", td_style),
                    Paragraph(f"{r.soil_ph:.1f}", td_style),
                    Paragraph(f"{r.light_intensity:.0f}", td_style)
                ])
            t_sensors = Table(sensor_table_data, colWidths=[130, 80, 80, 80, 60, 100])
            t_sensors.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('PADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))
            ]))
            story.append(t_sensors)
        else:
            story.append(Paragraph("No sensor telemetry logs recorded for this plant.", body_style))
        story.append(Spacer(1, 15))
        
        # Growth Predictions Table
        story.append(Paragraph("ML Growth Projections", h2_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7'), spaceAfter=10))
        
        if predictions:
            pred_headers = [
                Paragraph("Stage", th_style),
                Paragraph("Daily Rate (cm/d)", th_style),
                Paragraph("Height +7d (cm)", th_style),
                Paragraph("Height +30d (cm)", th_style),
                Paragraph("Harvest Date", th_style),
                Paragraph("Health Score", th_style)
            ]
            pred_table_data = [pred_headers]
            for p in predictions[:5]:
                pred_table_data.append([
                    Paragraph(p.current_stage, td_style),
                    Paragraph(f"{p.growth_rate:.3f}", td_style),
                    Paragraph(f"{p.height_7d:.2f}", td_style),
                    Paragraph(f"{p.height_30d:.2f}", td_style),
                    Paragraph(p.estimated_harvest.strftime('%Y-%m-%d'), td_style),
                    Paragraph(f"{p.health_score:.1f}%", td_style)
                ])
            t_preds = Table(pred_table_data, colWidths=[110, 90, 90, 90, 90, 70])
            t_preds.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16a085')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('PADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))
            ]))
            story.append(t_preds)
        else:
            story.append(Paragraph("No growth predictions calculated yet.", body_style))
        story.append(Spacer(1, 15))
        
        # Disease Diagnostics History Table
        story.append(Paragraph("Leaf Disease Diagnostic Logs", h2_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7'), spaceAfter=10))
        
        if diagnoses:
            diag_headers = [
                Paragraph("Timestamp", th_style),
                Paragraph("Diagnosis Name", th_style),
                Paragraph("Confidence", th_style),
                Paragraph("Severity", th_style),
                Paragraph("Treatment Fungicide", th_style),
                Paragraph("Recovery", th_style)
            ]
            diag_table_data = [diag_headers]
            for d in diagnoses[:5]:
                diag_table_data.append([
                    Paragraph(d.timestamp.strftime('%Y-%m-%d %H:%M'), td_style),
                    Paragraph(d.disease_name, td_style),
                    Paragraph(f"{d.confidence:.1f}%", td_style),
                    Paragraph(d.severity, td_style),
                    Paragraph(d.recommended_fungicide, td_style),
                    Paragraph(d.recovery_time, td_style)
                ])
            t_diag = Table(diag_table_data, colWidths=[100, 120, 70, 60, 110, 70])
            t_diag.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('PADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))
            ]))
            story.append(t_diag)
        else:
            story.append(Paragraph("No disease instances diagnosed for this plant.", body_style))
        story.append(Spacer(1, 20))
        
        # Report Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray, spaceBefore=20, spaceAfter=5))
        story.append(Paragraph("Disclaimer: This report was compiled automatically using machine learning algorithms. Keep crop verification records active and verify parameters manually in critical circumstances.", ParagraphStyle('Footer', fontSize=8, textColor=colors.gray, alignment=1)))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
