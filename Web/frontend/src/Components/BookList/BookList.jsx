import React, { useState, useEffect } from "react";
import axios from "axios";
import Tags from "../Tags/Tags";
import "../BookList/BookList.css";
import "../BookList/modal.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { BiSearch } from "react-icons/bi";
import ReactModal from "react-modal";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../Noti/Noti";
import { getAuthInfo } from "../LoginForm/auth";
import config from '../../config'; 

export default function BookList() {
  const [books, setBooks] = useState([]);
  const [selectedBooks, setSelectedBooks] = useState([]); // Danh sách sách được chọn
  const [selectedBook, setSelectedBook] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [SortOption, setSortOption] = useState("");
  const { role } = getAuthInfo();
  const { showNotification } = useNotification();

  // Hàm để lấy sách theo tag hoặc tất cả sách
  const fetchBooksByTag = async (tag) => {
    try {
      let response;
      if (tag === "" || tag === "all") {
        // Lấy tất cả sách
        response = await axios.get(`${config.apiUrl}/get_books_info`);
        setBooks(response.data.books_info);
      } else {
        // Lấy sách theo tag cụ thể
        response = await axios.get(
          `${config.apiUrl}/books_by_tag?tag=${tag}`
        );
        setBooks(response.data.books_list);
      }
    } catch (error) {
      console.error("Error fetching books:", error);
    }
  };

  useEffect(() => {
    fetchBooksByTag("");
  }, []);

  const handleSearchChange = async (event) => {
    const query = event.target.value;
    setSearchQuery(query);
    if (query.trim() !== "") {
      try {
        const lowerCaseQuery = query.toLowerCase();
        const response = await axios.get(
          `${config.apiUrl}/search_books?query=${lowerCaseQuery}`
        );
        setBooks(response.data.books);
      } catch (error) {
        console.error("Error fetching books based on search query:", error);
      }
    } else {
      fetchAllBooks();
    }
  };

  const handleSortChange = async (event) => {
    const sortOption = event.target.value;
    setSortOption(sortOption);
    if (sortOption !== "") {
      try {
        const response = await axios.get(
          `${config.apiUrl}/sort_books?sortOption=${sortOption}`
        );
        setBooks(response.data.books);
      } catch (error) {
        console.error("Error sorting books:", error);
      }
    } else {
      fetchAllBooks();
    }
  };

  const fetchAllBooks = async () => {
    try {
      const response = await axios.get(`${config.apiUrl}/get_books_info`);
      setBooks(response.data.books_info);
    } catch (error) {
      console.error("Error fetching all books:", error);
    }
  };

  // Hàm để mở modal và hiển thị thông tin chi tiết sách
  const handleBookClick = (book) => {
    setSelectedBook(book);
    setIsModalOpen(true);
  };

  // Hàm để đóng modal
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedBook(null);
  };

  const handleBookCheckboxChange = (book) => {
    if (selectedBooks.includes(book)) {
      // Nếu sách đã được chọn, bỏ chọn
      setSelectedBooks(selectedBooks.filter((b) => b !== book));
    } else {
      // Nếu sách chưa được chọn, chọn
      setSelectedBooks([...selectedBooks, book]);
    }
  };

  const navigate = useNavigate();

  const handleAddBook = () => {
    navigate("/home/createbook");
  };

  const handleEditBook = (bookId) => {
    navigate("/home/editbook", {
      state: { send_bookId: bookId },
    });
  };

  // Hàm xóa sách (ví dụ)
  const deleteBooks = async () => {
    if (selectedBooks.length === 0) {
      console.log("No books selected for deletion.");

      return;
    }
    console.log(selectedBooks); // Print selectedBooks to console
    const bookIds = selectedBooks.map((book) => book.id); // Retrieve book IDs

    try {
      const response = await axios.post(`${config.apiUrl}/delete_books`, {
        ids: bookIds,
      });

      if (response.data.success) {
        showNotification("Books deleted successfully.", "success");
        fetchAllBooks(); // Update the book list
        setSelectedBooks([]);
      } else {
        showNotification(
          "Failed to delete books:",
          response.data.message,
          "error"
        );
      }
    } catch (error) {
      showNotification("Error deleting books:", "error");
    }
  };

  return (
    <div className="booklist-page">
      <Tags onTagSelect={fetchBooksByTag} />

      <div className="search-sort-container">
        <div className="booklist-page-container">
          {role == 1 && (
            <div className="book-actions-1">
              <button onClick={handleAddBook}>Thêm sách</button>
              <button onClick={() => deleteBooks()}>Xóa sách</button>
            </div>
          )}
        </div>
        <div className="sort-column">
          <select
            className="sort-dropdown"
            value={SortOption}
            onChange={handleSortChange}
          >
            <option value="">Sắp xếp</option>
            <option value="name-asc">Tên (A-Z)</option>
            <option value="name-desc">Tên (Z-A)</option>
            <option value="quantity-asc">Số lượng (Tăng dần)</option>
            <option value="quantity-desc">Số lượng (Giảm dần)</option>
          </select>
        </div>
        <div className="search-box">
          <input
            type="text"
            placeholder="Tìm kiếm sách ..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="search-input"
          />
          <BiSearch className="search-icon" />
        </div>
      </div>
      <section className="card-container">
        {books.map((book, index) => (
          <section key={index} className="book-card">
            <img
              src={`data:image/png;base64,${book.book_image}`}
              className="card-img"
              alt="book cover"
            />
            <div className="card-details" onClick={() => handleBookClick(book)}>
              <div className="book-title">
                <h3>{book.book_name}</h3>
              </div>
              <div className="book-author">
                <span className="author-label">Tác giả:</span>
                <span className="author-name">{book.auth}</span>
              </div>
              <div className="book-quantity">
                <span className="quantity-label">Số lượng:</span>
                <span className="quantity-value">{book.quantity}</span>
              </div>
            </div>
            <div className="checkbox-container">
              <input
                type="checkbox"
                className="checkbox"
                checked={selectedBooks.includes(book)}
                onChange={() => handleBookCheckboxChange(book)}
              />
            </div>
          </section>
        ))}
      </section>

      <ReactModal
        isOpen={isModalOpen}
        onRequestClose={closeModal}
        contentLabel="Book Details"
        className="modal-content"
        overlayClassName="modal-overlay"
      >
        {selectedBook && (
          <div className="row">
            <div className="col-md-6">
              <img
                src={`data:image/png;base64,${selectedBook.book_image}`}
                alt="book cover"
                className="modal-image"
              />
            </div>
            <div className="col-md-6">
              <div className="book-title">
                <h3>{selectedBook.book_name}</h3>
              </div>
              <div className="book-author">
                <span className="author-label">Tác giả: </span>
                <span className="author-name">{selectedBook.auth}</span>
              </div>
              <div className="book-quantity">
                <span className="quantity-label">Số lượng: </span>
                <span className="quantity-value">{selectedBook.quantity}</span>
              </div>
              <div className="book-quantity">
                <span className="author-label">Mã sách: </span>
                <span className="author-value">{selectedBook.id}</span>
              </div>
              <div className="book-quantity">
                <span className="author-label">Tag: </span>
                <span className="author-value">{selectedBook.tag}</span>
              </div>
              <div className="book-quantity">
                <span className="author-label">Mô tả: </span>
                <span className="author-value">{selectedBook.description}</span>
              </div>

              <div className="modal-footer">
               
                {role == 1 && (
                  <button
                    className="edit-button-1"
                    onClick={() => handleEditBook(selectedBook.id)}
                  >
                    Sửa sách
                  </button>
                )}

                <button className="close-button-2" onClick={closeModal}>
                  Đóng
                </button>
              </div>
            </div>
          </div>
        )}
      </ReactModal>
    </div>
  );
}
