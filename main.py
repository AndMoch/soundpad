import sqlite3
import sys
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QDialog, QFileDialog, QTableWidgetItem, QMenu,\
                            QAction, QMessageBox
from soundpad import Ui_MainWindow
from addsound import Ui_Form
from sethotkey import Ui_Hotkey_choose

keymap = {}
for key, value in vars(Qt).items():
    if isinstance(value, Qt.Key):
        keymap[value] = key.partition('_')[2]

modmap = {
    Qt.ControlModifier: keymap[Qt.Key_Control],
    Qt.AltModifier: keymap[Qt.Key_Alt],
    Qt.ShiftModifier: keymap[Qt.Key_Shift],
    Qt.MetaModifier: keymap[Qt.Key_Meta],
    Qt.GroupSwitchModifier: keymap[Qt.Key_AltGr],
    Qt.KeypadModifier: keymap[Qt.Key_NumLock],
    }

# Функция, отвечающая за получение названия клавиши, или сочетания клавиш
def keyevent_to_string(event):
    sequence = []
    for modifier, text in modmap.items():
        if event.modifiers() & modifier:
            sequence.append(text)
    key = keymap.get(event.key(), event.text())
    if key not in sequence:
        sequence.append(key)
    return '+'.join(sequence)

# Далее идут классы ошибок
class RootCategoryChange(Exception):
    pass


class ObjectWithSuchNameAlreadyExist(Exception):
    pass


class EmptyName(Exception):
    pass


class SoundWithSuchNameAlreadyExist(Exception):
    pass


class KeyIsUsed(Exception):
    pass


class KeyLineIsEmpty(Exception):
    pass

# Класс основного виджета приложения
class SoundpadWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Soundpad")
        self.con = sqlite3.connect("sounds.db")
        self.cur = self.con.cursor()
        self.add_sound.clicked.connect(self.add_new_sound)
        self.add_category.clicked.connect(self.dialog_for_category_action)
        self.hotkeys_enabled = False
        self.adding_changing = False
        self.playing = False
        self.paused = False
        self.activate_hotkeys.clicked.connect(self.hotkeys_enable_disable)
        self.update_categories_table()
        self.update_all_sounds_table()
        self.categories_table.itemClicked.connect(self.category_chosen)
        self.categories_table.installEventFilter(self)
        self.sounds_table.installEventFilter(self)
        self.grabKeyboard()
        self.volume_slider.valueChanged.connect(self.volume_change)
        self.play_button.clicked.connect(self.play_sound)
        self.pause_button.clicked.connect(self.pause_sound)
        self.stop_button.clicked.connect(self.stop_sound)
        self.player = QMediaPlayer()
        self.player.setVolume(self.volume_slider.value())
        self.activateWindow()
        self.setFocus()

    # Вызов диалога для создания или изменения категорий
    def dialog_for_category_action(self, changing=False):
        try:
            if not self.adding_changing:
                self.adding_changing = True
                self.releaseKeyboard()
                if not changing:
                    name, ok_pressed = QInputDialog.getText(self, "Новая категория", "Введите имя")
                elif changing:
                    if self.categories_table.currentItem().text() == 'Все звуки':
                        raise RootCategoryChange
                    name, ok_pressed = QInputDialog.getText(self, "Переименовать категорию", "Введите новое имя")
                if ok_pressed:
                    if not changing:
                        if name in self.get_all_categories_names():
                            raise ObjectWithSuchNameAlreadyExist
                        elif name == '':
                            raise EmptyName
                        self.cur.execute("INSERT INTO Categories(name) VALUES(?)", (name,))
                        self.con.commit()
                    elif changing:
                        if name == '':
                            raise EmptyName
                        changed_name = self.categories_table.currentItem().text()

                        self.cur.execute("""UPDATE Categories SET name = ?
                                        WHERE name = ?""", (name, changed_name))
                        self.cur.execute("""UPDATE Sounds SET cat_name = ?
                                                            WHERE cat_name = ?""", (name, changed_name))
                        self.con.commit()
                self.update_categories_table()
                if not self.categories_table.selectedItems():
                    self.update_all_sounds_table()
                elif self.categories_table.currentItem().text() == "Все звуки":
                    self.update_all_sounds_table()
                else:
                    self.update_category_sounds_table(self.categories_table.currentItem().text())
                self.setFocus()
                self.grabKeyboard()
        except ObjectWithSuchNameAlreadyExist:
            cat_already_exist = QMessageBox(self)
            cat_already_exist.setText('Категория с таким именем уже существует')
            cat_already_exist.setWindowTitle('Ошибка!')
            cat_already_exist.exec_()
        except EmptyName:
            empty_cat_name = QMessageBox(self)
            empty_cat_name.setText('Пустое имя категории')
            empty_cat_name.setWindowTitle('Ошибка!')
            empty_cat_name.exec_()
        except RootCategoryChange:
            tried_change_root = QMessageBox(self)
            tried_change_root.setText('Нельзя изменять корневую категорию')
            tried_change_root.setWindowTitle('Ошибка!')
            tried_change_root.exec_()
        finally:
            self.adding_changing = False
            self.activateWindow()

    # Добавление звука, вызов окна добавления
    def add_new_sound(self):
        if not self.adding_changing:
            self.adding_changing = True
            add_widget = AddOrChangeSound()
            add_widget.show()
            add_widget.exec_()
            add_widget.activateWindow()
    
    # Обновление таблицы с категориями
    def update_categories_table(self):
        all_categories = self.cur.execute("""SELECT name FROM Categories""").fetchall()
        all_categories = [e[0] for e in all_categories]
        self.categories_table.setColumnCount(1)
        self.categories_table.setRowCount(len(all_categories))
        self.categories_table.setHorizontalHeaderLabels(['Категории'])
        for i, category in enumerate(all_categories):
            self.categories_table.setItem(i, 0, QTableWidgetItem(category))
    
    # Обновление таблицы со всеми звуками
    def update_all_sounds_table(self):
        self.sounds_table.setRowCount(0)
        all_sounds = self.cur.execute("""SELECT name, key, cat_name FROM Sounds""").fetchall()
        self.sounds_table.setColumnCount(3)
        self.sounds_table.setRowCount(len(all_sounds))
        self.sounds_table.setHorizontalHeaderLabels(['Название', 'Клавиша', 'Категория'])
        for i, sound in enumerate(all_sounds):
            for j, elem in enumerate(sound):
                self.sounds_table.setItem(i, j, QTableWidgetItem(elem))
    
    # Обновление таблицы со звуками, относящимися к выбранной категории
    def update_category_sounds_table(self, filecat):
        self.sounds_table.setRowCount(0)
        self.sounds_table.setColumnCount(2)
        cat_sounds = self.cur.execute("""SELECT name, key FROM Sounds WHERE cat_id=(SELECT id FROM Categories
                                         WHERE Categories.name = ?)""", (filecat,)).fetchall()
        self.sounds_table.setRowCount(len(cat_sounds))
        self.sounds_table.setHorizontalHeaderLabels(['Название', 'Клавиша'])
        for i, sound in enumerate(cat_sounds):
            for j, elem in enumerate(sound):
                self.sounds_table.setItem(i, j, QTableWidgetItem(str(elem)))
    
    # Выбор категории
    def category_chosen(self):
        filecat = self.sender().currentItem().text()
        if filecat == 'Все звуки':
            self.update_all_sounds_table()
        else:
            self.update_category_sounds_table(filecat)

    # Включение/выключение возможности использования горячих клавиш
    def hotkeys_enable_disable(self):
        if self.activate_hotkeys.isChecked():
            self.hotkeys_enabled = True
        else:
            self.hotkeys_enabled = False

    # Получение списка всех категорий
    def get_all_categories_names(self):
        categories = [e[0] for e in self.cur.execute("""SELECT name FROM Categories""").fetchall()]
        categories.append('Без категории')
        return categories

    # Получение списка всех имен звуков
    def get_all_sounds_names(self):
        return [e[0] for e in self.cur.execute("""SELECT name FROM Sounds""").fetchall()]

    # Получение списка всех использованных клавиш и их сочетаний
    def get_all_used_keys(self):
        return [e[0] for e in self.cur.execute("""SELECT key FROM Sounds WHERE key NOT NULL""").fetchall()]

    # Далее идут вызовы всплывающих окон ошибок
    def file_not_found_error(self):
        file_not_found = QMessageBox(self)
        file_not_found.setText('Файл не найден')
        file_not_found.setWindowTitle('Ошибка!')
        file_not_found.exec_()

    def sound_already_exist_error(self):
        sound_already_exist = QMessageBox(self)
        sound_already_exist.setText('Звук с таким именем уже существует')
        sound_already_exist.setWindowTitle('Ошибка!')
        sound_already_exist.exec_()

    def empty_sound_name_error(self):
        empty_sound_name = QMessageBox(self)
        empty_sound_name.setText('Пустое имя звука')
        empty_sound_name.setWindowTitle('Ошибка!')
        empty_sound_name.exec_()

    def key_is_used_error(self):
        key_is_used = QMessageBox(self)
        key_is_used.setText('Клавиша занята')
        key_is_used.setWindowTitle('Ошибка!')
        key_is_used.exec_()

    def key_line_empty_error(self):
        key_line_empty = QMessageBox(self)
        key_line_empty.setText('Нажмите на клавишу')
        key_line_empty.setWindowTitle('Ошибка!')
        key_line_empty.exec_()

    # Вызов контекстного меню и выполнение выбранного действия
    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.categories_table and not self.adding_changing:
            if self.categories_table.selectedItems():
                menu = QMenu()
                change_action = QAction('Переименовать категорию')
                menu.addAction(change_action)
                delete_action = QAction('Удалить категорию')
                menu.addAction(delete_action)
                action = menu.exec_(event.globalPos())
                if action == change_action:
                    self.change_category()
                elif action == delete_action:
                    self.delete_category()
        elif event.type() == QEvent.ContextMenu and source is self.sounds_table and not self.adding_changing:
            if self.sounds_table.selectedItems():
                menu = QMenu()
                change_action = QAction()
                delete_action = QAction()
                change_current_action = QAction()
                if self.sounds_table.currentItem().column() == 0:
                    change_action.setText('Изменить параметры звука')
                    menu.addAction(change_action)
                    change_current_action.setText('Переименовать звук')
                    menu.addAction(change_current_action)
                    delete_action.setText('Удалить звук')
                    menu.addAction(delete_action)
                    action = menu.exec_(event.globalPos())
                    if action == change_action:
                        self.change_sound()
                    elif action == change_current_action:
                        self.change_sound_name()
                    elif action == delete_action:
                        self.delete_sound()
                elif self.sounds_table.currentItem().column() == 1:
                    no_key = self.sounds_table.currentItem().text() == ''
                    if no_key:
                        change_action.setText('Привязать клавишу')
                        menu.addAction(change_action)
                    else:
                        change_current_action.setText('Изменить привязанную клавишу')
                        menu.addAction(change_current_action)
                        delete_action.setText('Отменить привязку к клавише')
                        menu.addAction(delete_action)
                    action = menu.exec_(event.globalPos())
                    if action == change_action:
                        self.set_hotkey_for_empty()
                    elif action == change_current_action:
                        self.set_new_hotkey()
                    elif action == delete_action:
                        self.clear_hotkey_line()
                elif self.sounds_table.currentItem().column() == 2:
                    if self.sounds_table.currentItem().text() == 'Без категории':
                        change_action.setText('Добавить звук в категорию')
                        menu.addAction(change_action)
                    else:
                        change_current_action.setText('Изменить категорию звука')
                        menu.addAction(change_current_action)
                        delete_action.setText('Убрать звук из категории')
                        menu.addAction(delete_action)
                    action = menu.exec_(event.globalPos())
                    if action == change_current_action:
                        self.change_or_add_sound_cat()
                    elif action == change_action:
                        self.change_or_add_sound_cat(True)
                    elif action == delete_action:
                        self.delete_sound_from_cat()
        return True
    
    # Переопределение метода на воспроизведение привязанного к клавише/сочетанию клавиш звука
    def keyPressEvent(self, event):
        if self.hotkeys_enabled:
            if keyevent_to_string(event) in self.get_all_used_keys():
                self.play_sound(True, key_pressed=keyevent_to_string(event))
    
    # Удаление категории и относящихся к ней звуков
    def delete_category(self):
        try:
            if self.categories_table.currentItem().text() == 'Все звуки':
                raise RootCategoryChange
            self.cur.execute("""DELETE FROM Categories WHERE name = ?""",
                             (self.categories_table.currentItem().text(),))
            self.cur.execute("""DELETE FROM Sounds WHERE cat_name = ?""",
                             (self.categories_table.currentItem().text(),))
            self.con.commit()
            if not self.categories_table.selectedItems():
                self.update_all_sounds_table()
            elif self.categories_table.currentItem().text() == "Все звуки":
                self.update_all_sounds_table()
            else:
                self.update_category_sounds_table(self.categories_table.currentItem().text())
            self.update_categories_table()
        except RootCategoryChange:
            tried_del_root = QMessageBox(self)
            tried_del_root.setText('Нельзя удалить корневую категорию')
            tried_del_root.setWindowTitle('Ошибка!')
            tried_del_root.exec_()
    
    # Вызов диалога для изменения категории
    def change_category(self):
        if not self.adding_changing:
            self.dialog_for_category_action(True)
    
    # Удаление звука
    def delete_sound(self):
        self.cur.execute("""DELETE FROM Sounds WHERE name = ?""", (self.sounds_table.currentItem().text(), ))
        self.con.commit()
        if not self.categories_table.selectedItems():
            self.update_all_sounds_table()
        elif self.categories_table.currentItem().text() == "Все звуки":
            self.update_all_sounds_table()
        else:
            self.update_category_sounds_table(self.categories_table.currentItem().text())

    # Смена параметров звука, вызов окна изменения
    def change_sound(self):
        if not self.adding_changing:
            self.adding_changing = True
            change_widget = AddOrChangeSound(True, old_name=self.sounds_table.currentItem().text())
            change_widget.show()
            change_widget.exec_()
            change_widget.activateWindow()
    
    # Изменение имени звука
    def change_sound_name(self):
        try:
            if not self.adding_changing:
                self.adding_changing = True
                self.releaseKeyboard()
                name, ok_pressed = QInputDialog.getText(self, "Переименовать звук", "Введите новое имя")
                if ok_pressed:
                    if name in ex.get_all_sounds_names():
                        raise ObjectWithSuchNameAlreadyExist
                    elif name == '':
                        raise EmptyName
                    old_name = self.sounds_table.currentItem().text()
                    self.cur.execute("""UPDATE Sounds SET name = ? WHERE name = ?""", (name, old_name))
                    self.con.commit()
                if not self.categories_table.selectedItems():
                    self.update_all_sounds_table()
                elif self.categories_table.currentItem().text() == "Все звуки":
                    self.update_all_sounds_table()
                else:
                    self.update_category_sounds_table(self.categories_table.currentItem().text())
                self.grabKeyboard()
        except ObjectWithSuchNameAlreadyExist:
            self.sound_already_exist_error()
        except EmptyName:
            self.empty_sound_name_error()
        finally:
            self.adding_changing = False

    # Установка горячей клавиши/сочетания клавиш для звука с пустым параметром
    def set_hotkey_for_empty(self):
        if not self.adding_changing:
            self.adding_changing = True
            hotkey_widget = SetHotkey('', '', QDialog(), set_empty=True)
            hotkey_widget.show()
            hotkey_widget.exec_()
    
    # Смена горячей клавиши/сочетания клавиш звука
    def set_new_hotkey(self):
        if not self.adding_changing:
            self.adding_changing = True
            hotkey_widget = SetHotkey('', '', QDialog(), change_exist=True)
            hotkey_widget.show()
            hotkey_widget.exec_()

    # Отмена привязки клавиши/сочетания клавиш к звуку
    def clear_hotkey_line(self):
        self.cur.execute("""UPDATE Sounds SET key = ? WHERE key = ?""", ('', self.sounds_table.currentItem().text()))
        self.con.commit()
        if not self.categories_table.selectedItems():
            self.update_all_sounds_table()
        elif self.categories_table.currentItem().text() == "Все звуки":
            self.update_all_sounds_table()
        else:
            self.update_category_sounds_table(self.categories_table.currentItem().text())
    
    # Вызов диалога для изменения категории звука или добавления звука без категории в категорию
    def change_or_add_sound_cat(self, adding=False):
        if not self.adding_changing:
            self.adding_changing = True
            self.releaseKeyboard()
            if adding:
                if self.get_all_categories_names()[1:-1]:
                    category, ok = QInputDialog.getItem(self, "Добавить в категорию", "Категория",
                                                        self.get_all_categories_names()[1:-1], 1, False)
                else:
                    category, ok = QInputDialog.getItem(self, "Добавить в категорию", "Категория",
                                                        ['Без категории'], 1, False)
            else:
                if self.get_all_categories_names()[1:-1]:
                    category, ok = QInputDialog.getItem(self, "Изменить категорию", "Категория",
                                                        self.get_all_categories_names()[1:-1], 1, False)
                else:
                    category, ok = QInputDialog.getItem(self, "Изменить категорию", "Категория",
                                                        ['Без категории'], 1, False)
            if ok:
                if self.get_all_categories_names()[1:-1]
                    cat_id = int(ex.cur.execute("""SELECT id FROM Categories
                                                  WHERE name = ?""", (category,)).fetchone()[0])
                    self.cur.execute("""UPDATE Sounds SET cat_id = ? WHERE name = ?""",
                                     (cat_id, self.sounds_table.item(self.sounds_table.currentItem().row(), 0).text()))
                    self.cur.execute("""UPDATE Sounds SET cat_name = ? WHERE name = ?""",
                                     (category, self.sounds_table.item(self.sounds_table.currentItem().row(), 0).text()))
                    self.con.commit()
                if not self.categories_table.selectedItems():
                    self.update_all_sounds_table()
                elif self.categories_table.currentItem().text() == "Все звуки":
                    self.update_all_sounds_table()
                else:
                    self.update_category_sounds_table(self.categories_table.currentItem().text())
        self.adding_changing = False
        self.grabKeyboard()
    
    # Удаление звука из категории
    def delete_sound_from_cat(self):
        self.cur.execute("""UPDATE Sounds SET cat_id = 0, cat_name = 'Без категории' WHERE name = ?""",
                         (self.sounds_table.item(self.sounds_table.currentItem().row(), 0).text(),))
        self.con.commit()
        if not self.categories_table.selectedItems():
            self.update_all_sounds_table()
        elif self.categories_table.currentItem().text() == "Все звуки":
            self.update_all_sounds_table()
        else:
            self.update_category_sounds_table(self.categories_table.currentItem().text())
    
    # Возпроизведение звука
    def play_sound(self, by_hotkey=False, key_pressed=''):
        try:
            if by_hotkey:
                file = self.cur.execute("""SELECT path FROM Sounds WHERE key = ?""",
                                        (key_pressed,)).fetchone()[0]
                for_not_found = open(file)
                media = QUrl.fromLocalFile(file)
                content = QMediaContent(media)
                self.player.setMedia(content)
                self.player.play()
            else:
                if not self.paused:
                    if self.sounds_table.selectedItems():
                        file = self.cur.execute("""SELECT path FROM Sounds WHERE name = ?""",
                                                (self.sounds_table.item(self.sounds_table.currentItem().row(),
                                                0).text(),)).fetchone()[0]
                    else:
                        file = self.cur.execute("""SELECT path FROM Sounds WHERE name = ?""",
                                                (self.sounds_table.item(0, 0).text(),)).fetchone()[0]
                    for_not_found = open(file)
                    media = QUrl.fromLocalFile(file)
                    content = QMediaContent(media)
                    self.player.setMedia(content)
                self.player.play()
                self.paused = False
        except FileNotFoundError:
            self.file_not_found_error()
    
    # Пауза
    def pause_sound(self):
        if self.player.state() is not QMediaPlayer.PlayingState:
            self.player.pause()
            self.paused = True
    
    # Остановка воспроизведения
    def stop_sound(self):
        self.player.stop()
    
    # Изменение громкости приложения 
    def volume_change(self):
        self.player.setVolume(self.volume_slider.value())

# Класс виджета добавления/изменения звука
class AddOrChangeSound(QDialog, Ui_Form):
    def __init__(self, changing=False, old_name=''):
        super().__init__()
        self.setupUi(self)
        self.changing = changing
        self.old_name = old_name
        ex.releaseKeyboard()
        if self.changing:
            self.setWindowTitle("Смена параметров")
        else:
            self.setWindowTitle("Новый звук")
        all_categories = ex.get_all_categories_names()[1:]
        self.category_choose.addItems(all_categories)
        self.ok_button.clicked.connect(self.agreed_to_add)
        self.cancel_button.clicked.connect(self.disagreed_to_add)
    
    # Добавление/изменение звука 
    def agreed_to_add(self):
        file_name = self.file_name.text()
        file_category = self.category_choose.currentText()
        if self.set_hotkey.isChecked():
            if self.changing:
                hotkey_widget = SetHotkey(file_name, file_category, self, change_sound=True, old_name=self.old_name)
            else:
                hotkey_widget = SetHotkey(file_name, file_category, self)
            hotkey_widget.show()
            hotkey_widget.exec_()
            hotkey_widget.activateWindow()
        else:
            try:
                if file_name in ex.get_all_sounds_names() and not self.changing:
                    raise ObjectWithSuchNameAlreadyExist
                elif file_name == '':
                    raise EmptyName
                filepath = QFileDialog.getOpenFileName(self, 'Выбрать звуковой файл', '',
                                                       'Аудио (*.mp3);;Аудио (*.wav)')[0]
                if file_category == 'Без категории':
                    cat_id = 0
                else:
                    cat_id = int(ex.cur.execute("""SELECT id FROM Categories
                                                WHERE name = ?""", (file_category,)).fetchone()[0])
                if self.changing:
                    ex.cur.execute("""UPDATE Sounds SET name = ?, path = ?, key = ?, cat_id = ?, cat_name = ?
                                      WHERE name = ?""",
                                   (file_name, filepath, '', cat_id, file_category, self.old_name))
                else:
                    ex.cur.execute("""INSERT INTO Sounds(name, path, key, cat_id, cat_name)
                                      VALUES (?, ?, ?, ?, ?)""", (file_name, filepath, '', cat_id, file_category))
                ex.con.commit()
                if not ex.categories_table.selectedItems():
                    ex.update_all_sounds_table()
                elif ex.categories_table.currentItem().text() == "Все звуки":
                    ex.update_all_sounds_table()
                else:
                    ex.update_category_sounds_table(ex.categories_table.currentItem().text())
                self.close()
                ex.adding_changing = False
                ex.grabKeyboard()
            except ObjectWithSuchNameAlreadyExist:
                ex.sound_already_exist_error()
            except EmptyName:
                ex.empty_sound_name_error()
            finally:
                self.activateWindow()
    
    # Отказ
    def disagreed_to_add(self):
        self.close()

    def closeEvent(self, event):
        self.close()
        ex.adding_changing = False
        self.releaseKeyboard()
        ex.grabKeyboard()


# Класс виджета назначения горячей клавиши/сочетания клавиш для звука
class SetHotkey(QDialog, Ui_Hotkey_choose):
    def __init__(self, filename, filecat, widg, change_sound=False, old_name='', change_exist=False, set_empty=False):
        super().__init__()
        self.setupUi(self)
        self.change_sound = change_sound
        self.change_exist = change_exist
        self.set_for_empty = set_empty
        if self.change_sound or self.set_for_empty or self.change_exist:
            self.setWindowTitle("Установить новую горячую клавишу")
        else:
            self.setWindowTitle("Установить горячую клавишу")
        self.ok_button.clicked.connect(self.agreed_to_add)
        self.cancel_button.clicked.connect(self.disagreed_to_add)
        self.file_name = filename
        self.file_category = filecat
        self.old_name = old_name
        self.to_close = widg
        self.grabKeyboard()
    
    # Назначения горячей клавиши/сочетания клавиш для звука
    def agreed_to_add(self):
        try:
            if self.change_sound or (not self.change_sound and not self.change_exist and not self.set_for_empty):
                if self.file_name in ex.get_all_sounds_names() and not self.change_sound:
                    raise ObjectWithSuchNameAlreadyExist
                elif self.file_name == '':
                    raise EmptyName
            if self.key_line.text() == '':
                raise KeyLineIsEmpty
            elif self.key_line.text() in ex.get_all_used_keys():
                raise KeyIsUsed
            if not self.set_for_empty and not self.change_exist:
                filepath = QFileDialog.getOpenFileName(self, 'Выбрать звуковой файл', '',
                                                       'Аудио (*.mp3);;Аудио (*.wav)')[0]
                if self.file_category == 'Без категории':
                    cat_id = 0
                else:
                    cat_id = int(ex.cur.execute("""SELECT id FROM Categories
                                                WHERE name = ?""", (self.file_category,)).fetchone()[0])
            if self.change_sound:
                ex.cur.execute("""UPDATE Sounds SET name = ?, path = ?, key = ?, cat_id = ?,
                               cat_name = ? WHERE name = ?""",
                               (self.file_name, filepath, self.key_line.text(), cat_id, self.file_category,
                                self.old_name))
            elif self.set_for_empty or self.change_exist:
                ex.cur.execute("""UPDATE Sounds SET key = ? WHERE name = ?""",
                               (self.key_line.text(),
                                ex.sounds_table.item(ex.sounds_table.currentItem().row(), 0).text()))
            else:
                ex.cur.execute("""INSERT INTO Sounds(name, path, key, cat_id, cat_name) VALUES (?, ?, ?, ?, ?)""",
                               (self.file_name, filepath, self.key_line.text(), cat_id, self.file_category))
            ex.con.commit()
            self.close()
            self.to_close.close()
            if not ex.categories_table.selectedItems():
                ex.update_all_sounds_table()
            elif ex.categories_table.currentItem().text() == "Все звуки":
                ex.update_all_sounds_table()
            else:
                ex.update_category_sounds_table(ex.categories_table.currentItem().text())
            ex.adding_changing = False
            self.releaseKeyboard()
            ex.grabKeyboard()
        except ObjectWithSuchNameAlreadyExist:
            ex.sound_already_exist_error()
        except EmptyName:
            ex.empty_sound_name_error()
        except KeyIsUsed:
            ex.key_is_used_error()
        except KeyLineIsEmpty:
            ex.key_line_empty_error()
        finally:
            if self.change_sound or not self.change_sound and not self.set_for_empty and not self.change_exist:
                self.to_close.activateWindow()
            self.activateWindow()

    def disagreed_to_add(self):
        self.close()
    
    # Получение названия нажатой клавиши/сочетания клавиш
    def keyPressEvent(self, event):
        self.key_line.setText(keyevent_to_string(event))

    def closeEvent(self, event):
        self.close()
        ex.adding_changing = False
        self.releaseKeyboard()
        ex.grabKeyboard()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SoundpadWidget()
    ex.show()
    sys.exit(app.exec_())
