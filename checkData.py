import datetime

class TempDataStorage:
    def __init__(self):
        self.data = {}  # Sử dụng dictionary để lưu trữ dữ liệu của một sinh viên

    def add_student_data(self, student_id):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data = {
            'student_id': student_id,
            'time_in': current_time,
            'time_out': None,
            'is_borrow': True,
            'books': {}  # Khởi tạo dictionary books rỗng
        }

    def update_student_data(self, time_out, is_borrow, books):
        # Không cần kiểm tra student_id vì chỉ có một sinh viên
        self.data['time_out'] = time_out
        self.data['is_borrow'] = is_borrow
        self.data['books'] = books

    def get_student_data(self):  # Không cần tham số student_id
        return self.data

    def check_student_data(self):  # Không cần tham số student_id
        return bool(self.data)  # Kiểm tra xem dictionary có rỗng hay không

    def get_all_data(self):
        return self.data

    def clear_data(self):
        self.data = {}
