import sqlite3
import json
from PyQt6.QtWidgets import (QWidget, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, 
                             QTreeWidgetItem, QScrollArea, QLabel, QTableWidget, QTableWidgetItem,
                             QDateEdit, QLineEdit, QPushButton, QHeaderView, QFileDialog)
from PyQt6.uic import loadUi
from PyQt6.QtCore import QDate, Qt
import matplotlib.pyplot as plt

# Utilisation de backend_qtagg (spécifique à PyQt6)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from utils import resource_path
from GestionHistorique import GestionHistorique 

class GestionCarburant(QWidget):
    def __init__(self, db_connect_func, role_utilisateur="Administrateur"):
        super().__init__()
        loadUi(resource_path("GestionCarburant.ui"), self)
        
        self.db_connect = db_connect_func
        self.role_utilisateur = role_utilisateur

        # Initialisation de la date du jour
        self.input_date.setDate(QDate.currentDate())
        
        # Connexion des boutons
        self.btn_nouveau.clicked.connect(self.nouveau_enregistrement)
        self.btn_ajouter_plein.clicked.connect(self.enregistrer_plein)
        self.btn_modifier.clicked.connect(self.modifier_plein)
        self.btn_supprimer.clicked.connect(self.supprimer_plein)
        self.btn_stats.clicked.connect(self.afficher_graphique)
        
        # Connexion du tableau
        self.tableCarburant.itemSelectionChanged.connect(self.charger_champs)

        # Restriction des droits
        if self.role_utilisateur == "Employe":
            self.btn_modifier.setVisible(False)
            self.btn_supprimer.setVisible(False)

        self.charger_vehicules()
        self.load_pleins()

    def nouveau_enregistrement(self):
        self.tableCarburant.clearSelection()
        self.combo_vehicule.setCurrentIndex(0)
        self.input_date.setDate(QDate.currentDate())
        self.input_montant.clear()
        
        if hasattr(self, 'input_volume'): self.input_volume.clear()
        if hasattr(self, 'input_litres'): self.input_litres.clear()
        
        self.combo_vehicule.setFocus()

    def charger_champs(self):
        selected = self.tableCarburant.currentItem()
        if not selected: return
        
        immat = selected.text(1)
        date_str = selected.text(2)
        montant = selected.text(3)
        volume = selected.text(4)
        
        index = self.combo_vehicule.findData(immat)
        if index >= 0: self.combo_vehicule.setCurrentIndex(index)
        
        self.input_date.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
        self.input_montant.setText(montant)
        
        if hasattr(self, 'input_volume'): self.input_volume.setText(volume)
        if hasattr(self, 'input_litres'): self.input_litres.setText(volume)

    def charger_vehicules(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT immatriculation, marque FROM VEHICULE ORDER BY immatriculation")
            self.combo_vehicule.clear()
            self.combo_vehicule.addItem("Sélectionner un véhicule...", "")
            for immat, marque in cursor.fetchall():
                self.combo_vehicule.addItem(f"{immat} - {marque}", immat)
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def load_pleins(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_plein, immatriculation, date_plein, montant, litres 
                FROM CONSOMMATION_CARBURANT 
                ORDER BY date_plein DESC, id_plein DESC
            """)
            self.tableCarburant.clear()
            self.tableCarburant.setHeaderLabels(["ID", "Immatriculation", "Date", "Montant (€)", "Volume (L)"])
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableCarburant)
                item.setText(0, str(row[0]))
                item.setData(0, Qt.ItemDataRole.UserRole, row[0]) 
                item.setText(1, str(row[1]))
                item.setText(2, str(row[2]))
                item.setText(3, f"{row[3]:.2f}")
                item.setText(4, f"{row[4]:.2f}")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def enregistrer_plein(self):
        immat = self.combo_vehicule.currentData()
        date_p = self.input_date.date().toString("yyyy-MM-dd")
        montant_str = self.input_montant.text().strip().replace(',', '.')
        
        volume_str = ""
        if hasattr(self, 'input_volume'): volume_str = self.input_volume.text().strip().replace(',', '.')
        elif hasattr(self, 'input_litres'): volume_str = self.input_litres.text().strip().replace(',', '.')

        if not immat: return QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un véhicule.")
        if not montant_str or not volume_str: return QMessageBox.warning(self, "Erreur", "Le montant et le volume sont obligatoires.")

        try:
            montant, volume = float(montant_str), float(volume_str)
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO CONSOMMATION_CARBURANT (date_plein, montant, litres, immatriculation) VALUES (?, ?, ?, ?)", (date_p, montant, volume, immat))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, self.role_utilisateur, "Saisie Carburant", f"Plein de {volume}L ({montant}€) pour {immat}")
            QMessageBox.information(self, "Succès", "Le plein a été enregistré avec succès.")
            
        except ValueError:
            return QMessageBox.warning(self, "Erreur", "Format numérique invalide.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur BDD", f"Erreur : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

        self.load_pleins()
        self.nouveau_enregistrement()

    def modifier_plein(self):
        selected = self.tableCarburant.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez un plein à modifier.")
        
        id_plein = selected.data(0, Qt.ItemDataRole.UserRole)
        immat = self.combo_vehicule.currentData()
        date_p = self.input_date.date().toString("yyyy-MM-dd")
        montant_str = self.input_montant.text().strip().replace(',', '.')
        
        volume_str = ""
        if hasattr(self, 'input_volume'): volume_str = self.input_volume.text().strip().replace(',', '.')
        elif hasattr(self, 'input_litres'): volume_str = self.input_litres.text().strip().replace(',', '.')

        try:
            montant, volume = float(montant_str), float(volume_str)
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE CONSOMMATION_CARBURANT SET date_plein=?, montant=?, litres=?, immatriculation=? WHERE id_plein=?", (date_p, montant, volume, immat, id_plein))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, self.role_utilisateur, "Modif. Carburant", f"Plein ID {id_plein} modifié.")
            QMessageBox.information(self, "Succès", "Plein mis à jour avec succès.")
        except ValueError:
            return QMessageBox.warning(self, "Erreur", "Format numérique invalide.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_pleins()

    def supprimer_plein(self):
        selected = self.tableCarburant.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez un plein à supprimer.")
        
        id_plein = selected.data(0, Qt.ItemDataRole.UserRole)
        if QMessageBox.question(self, 'Confirmation', "Êtes-vous sûr de vouloir supprimer ce plein ?") == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM CONSOMMATION_CARBURANT WHERE id_plein=?", (id_plein,))
                conn.commit()
                
                GestionHistorique.ajouter_log(self.db_connect, self.role_utilisateur, "Suppression Carburant", f"Plein ID {id_plein} supprimé.")
            except sqlite3.Error as e:
                print(e)
            finally:
                if 'conn' in locals() and conn: conn.close()
                
            self.load_pleins()
            self.nouveau_enregistrement()

    def afficher_graphique(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            
            # Récupération de la Marque et du Modèle en plus de l'immatriculation
            cursor.execute("""
                SELECT 
                    C.immatriculation, 
                    V.marque, 
                    V.modele, 
                    SUM(C.montant) as total, 
                    MIN(C.date_plein), 
                    MAX(C.date_plein)
                FROM CONSOMMATION_CARBURANT C
                JOIN VEHICULE V ON C.immatriculation = V.immatriculation
                GROUP BY C.immatriculation
            """)
            
            resultats = cursor.fetchall()
            
            if hasattr(self, 'graphe_dialog') and self.graphe_dialog.isVisible():
                self.graphe_dialog.close()

            if not resultats:
                return QMessageBox.information(self, "Information", "Aucune donnée de carburant n'est encore enregistrée.")

            vehicules_info = []
            labels = []
            depenses = []
            self.bar_data = [] 
            
            for row in resultats:
                immat, marque, modele, total, d_min, d_max = row
                vehicules_info.append({'immat': immat, 'marque': marque, 'modele': modele})
                
                try:
                    date_debut = d_min[:10].split('-')
                    date_fin = d_max[:10].split('-')
                    d1_fr = f"{date_debut[2]}/{date_debut[1]}/{date_debut[0]}"
                    d2_fr = f"{date_fin[2]}/{date_fin[1]}/{date_fin[0]}"
                    
                    if d1_fr == d2_fr:
                        chaine_date = f"Le {d1_fr}"
                    else:
                        chaine_date = f"Du {d1_fr}\nau {d2_fr}" 
                except:
                    chaine_date = ""

                labels.append(f"{immat}\n({marque} {modele})\n{chaine_date}")
                depenses.append(total)

            self.graphe_dialog = QDialog(self)
            self.graphe_dialog.setWindowTitle("Analyse des dépenses en carburant (Interactif)")
            self.graphe_dialog.resize(900, 650) 
            layout = QVBoxLayout(self.graphe_dialog)

            # 🚀 ZONE DE DÉFILEMENT (SCROLL)
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)

            # Largeur dynamique : plus il y a de voitures, plus le graphique s'élargit
            largeur_fig = max(8, len(labels) * 2.5) 
            fig, self.ax = plt.subplots(figsize=(largeur_fig, 6))
            
            couleurs_base = ['#8e44ad', '#3498db', '#2ecc71', '#e67e22', '#e74c3c']
            couleurs = [couleurs_base[i % len(couleurs_base)] for i in range(len(labels))]
            
            bars = self.ax.bar(labels, depenses, color=couleurs)
            
            self.tooltip = self.ax.annotate(
                "", xy=(0,0), xytext=(15, 15),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="#fdfde3", ec="black", lw=1),
                fontsize=10, zorder=100
            )
            self.tooltip.set_visible(False)

            for i, bar in enumerate(bars):
                hauteur = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., hauteur + 1,
                        f'{hauteur:.2f}€', ha='center', va='bottom', fontsize=10, fontweight='bold')
                
                v = vehicules_info[i]
                self.bar_data.append({
                    'bar': bar,
                    'immat': v['immat'],
                    'marque': v['marque'],
                    'modele': v['modele'],
                    'info': f"VÉHICULE : {v['immat']}\n{v['marque']} {v['modele']}\nCoût Total : {hauteur:.2f} €\n(Cliquez pour corriger un plein)"
                })

            self.ax.set_title("Dépenses totales en carburant par véhicule", fontsize=14, fontweight='bold', color='#2c3e50', pad=20)
            self.ax.set_ylabel("Montant Total (€)", fontweight='bold')
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            plt.xticks(rotation=0, fontsize=9)
            plt.tight_layout() 

            self.canvas = FigureCanvas(fig)
            # Hauteur et largeur minimales pour forcer l'apparition des barres de défilement
            largeur_min_px = max(800, len(labels) * 250)
            self.canvas.setMinimumSize(largeur_min_px, 500)
            
            self.canvas.mpl_connect("motion_notify_event", self.on_hover_graphe)
            self.canvas.mpl_connect("button_press_event", self.on_click_graphe)
            
            scroll_area.setWidget(self.canvas)

            # BOUTONS D'EXPORTATION
            layout_boutons = QHBoxLayout()
            
            btn_export_jpeg = QPushButton("📷 Exporter vers JPEG")
            btn_export_jpeg.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
            
            btn_export_png = QPushButton("🖼️ Exporter vers PNG")
            btn_export_png.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
            
            btn_export_json = QPushButton("📄 Exporter vers JSON")
            btn_export_json.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")

            layout_boutons.addWidget(btn_export_jpeg)
            layout_boutons.addWidget(btn_export_png)
            layout_boutons.addWidget(btn_export_json)
            
            layout.addLayout(layout_boutons)

            def exporter_image(format_img):
                fichier, _ = QFileDialog.getSaveFileName(self.graphe_dialog, f"Enregistrer l'image en {format_img.upper()}", f"Analyse_Carburant.{format_img}", f"Images (*.{format_img})")
                if fichier:
                    try:
                        fig.savefig(fichier, format=format_img, bbox_inches='tight', dpi=300)
                        QMessageBox.information(self.graphe_dialog, "Succès", f"Graphique exporté avec succès en {format_img.upper()} !")
                        GestionHistorique.ajouter_log(self.db_connect, self.role_utilisateur, "Export Graphique", f"Exportation du graphique carburant en {format_img.upper()}")
                    except Exception as e:
                        QMessageBox.critical(self.graphe_dialog, "Erreur", f"Échec de l'exportation : {e}")

            def exporter_json():
                fichier, _ = QFileDialog.getSaveFileName(self.graphe_dialog, "Enregistrer les données en JSON", "Donnees_Carburant.json", "Fichiers JSON (*.json)")
                if fichier:
                    try:
                        donnees = []
                        for row in resultats:
                            donnees.append({
                                "immatriculation": row[0],
                                "marque": row[1],
                                "modele": row[2],
                                "montant_total_euros": round(row[3], 2),
                                "premier_plein": row[4],
                                "dernier_plein": row[5]
                            })
                        
                        with open(fichier, 'w', encoding='utf-8') as f:
                            json.dump(donnees, f, indent=4, ensure_ascii=False)
                            
                        QMessageBox.information(self.graphe_dialog, "Succès", "Données exportées avec succès en JSON !")
                        GestionHistorique.ajouter_log(self.db_connect, self.role_utilisateur, "Export JSON", "Exportation des données carburant.")
                    except Exception as e:
                        QMessageBox.critical(self.graphe_dialog, "Erreur", f"Échec de l'exportation JSON : {e}")

            btn_export_jpeg.clicked.connect(lambda: exporter_image('jpeg'))
            btn_export_png.clicked.connect(lambda: exporter_image('png'))
            btn_export_json.clicked.connect(exporter_json)

            self.graphe_dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur BDD", f"Impossible de générer le graphique : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

    def on_hover_graphe(self, event):
        if event.inaxes == self.ax:
            for data in self.bar_data:
                cont, _ = data['bar'].contains(event)
                if cont:
                    self.tooltip.xy = (event.xdata, event.ydata)
                    self.tooltip.set_text(data['info'])
                    self.tooltip.set_visible(True)
                    self.canvas.draw_idle()
                    return
            if self.tooltip.get_visible():
                self.tooltip.set_visible(False)
                self.canvas.draw_idle()

    def on_click_graphe(self, event):
        if event.inaxes == self.ax and event.button == 1:
            for data in self.bar_data:
                cont, _ = data['bar'].contains(event)
                if cont:
                    self.ouvrir_popup_correction(data['immat'], data['marque'], data['modele'])
                    break

    def ouvrir_popup_correction(self, immat, marque, modele):
        dialog = QDialog(self.graphe_dialog)
        dialog.setWindowTitle(f"Correction de carburant - {immat}")
        dialog.resize(550, 400)
        layout = QVBoxLayout(dialog)
        
        lbl = QLabel(f"🚗 <b>Détails Carburant : {marque} {modele} ({immat})</b><br>Sélectionnez la ligne contenant l'erreur pour la modifier :")
        lbl.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(lbl)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID Plein", "Date", "Montant (€)", "Volume (L)"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                border: 1px solid #34495e;
                padding: 4px;
            }
        """)
        
        layout.addWidget(table)
        
        form_layout = QHBoxLayout()
        edit_date = QDateEdit()
        edit_date.setCalendarPopup(True)
        edit_montant = QLineEdit()
        edit_litres = QLineEdit()
        
        form_layout.addWidget(QLabel("Date :"))
        form_layout.addWidget(edit_date)
        form_layout.addWidget(QLabel("Montant (€) :"))
        form_layout.addWidget(edit_montant)
        form_layout.addWidget(QLabel("Litres :"))
        form_layout.addWidget(edit_litres)
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("💾 Enregistrer la correction")
        btn_save.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        layout.addWidget(btn_save)

        def charger_donnees():
            conn = self.db_connect()
            c = conn.cursor()
            c.execute("SELECT id_plein, date_plein, montant, litres FROM CONSOMMATION_CARBURANT WHERE immatriculation=? ORDER BY date_plein DESC", (immat,))
            rows = c.fetchall()
            table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                table.setItem(i, 0, QTableWidgetItem(str(r[0])))
                table.setItem(i, 1, QTableWidgetItem(str(r[1])))
                table.setItem(i, 2, QTableWidgetItem(str(r[2])))
                table.setItem(i, 3, QTableWidgetItem(str(r[3])))
            conn.close()

        charger_donnees()

        def on_select():
            sel = table.currentItem()
            if sel:
                row = sel.row()
                edit_date.setDate(QDate.fromString(table.item(row, 1).text(), "yyyy-MM-dd"))
                edit_montant.setText(table.item(row, 2).text())
                edit_litres.setText(table.item(row, 3).text())
        
        table.itemSelectionChanged.connect(on_select)

        if table.rowCount() > 0:
            table.selectRow(0)

        def save_data():
            sel = table.currentItem()
            if not sel:
                return QMessageBox.warning(dialog, "Erreur", "Veuillez d'abord sélectionner une ligne dans le tableau.")
            
            id_plein = table.item(sel.row(), 0).text()
            d = edit_date.date().toString("yyyy-MM-dd")
            m = edit_montant.text().replace(',', '.')
            l = edit_litres.text().replace(',', '.')
            
            try:
                conn = self.db_connect()
                c = conn.cursor()
                c.execute("UPDATE CONSOMMATION_CARBURANT SET date_plein=?, montant=?, litres=? WHERE id_plein=?", (d, float(m), float(l), id_plein))
                conn.commit()
                conn.close()
                QMessageBox.information(dialog, "Succès", "La correction a été appliquée avec succès !")
                GestionHistorique.ajouter_log(self.db_connect, self.role_utilisateur, "Modif. Carburant Rapide", f"Facture {id_plein} modifiée via le graphique.")
                dialog.accept() 
                
                self.load_pleins()          
                self.graphe_dialog.close()  
                self.afficher_graphique()   
                
            except ValueError:
                QMessageBox.warning(dialog, "Erreur", "Le montant et les litres doivent être des nombres.")
            except Exception as e:
                print(e)
                
        btn_save.clicked.connect(save_data)
        dialog.exec()