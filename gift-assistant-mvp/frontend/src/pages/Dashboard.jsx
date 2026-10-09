import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, clearToken } from "../api/client";
import VkImportButton from "../components/VkImportButton";

export default function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [csvFile, setCsvFile] = useState(null);
  const [csvMessage, setCsvMessage] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    setLoading(true);
    setError("");

    try {
      const [meData, recipientsData] = await Promise.all([
        api.me(),
        api.listRecipients()
      ]);
      setUser(meData);
      setRecipients(recipientsData);
    } catch (err) {
      setError(err.message);
      clearToken();
      navigate("/login");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (id) => {
    const confirmed = window.confirm("Удалить получателя?");
    if (!confirmed) return;

    try {
      await api.deleteRecipient(id);
      setRecipients((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCsvUpload = async () => {
    if (!csvFile) {
      setCsvMessage("Выберите CSV файл");
      return;
    }

    try {
      const result = await api.uploadProductsCsv(csvFile);
      setCsvMessage(`Импортировано товаров: ${result.imported}`);
    } catch (err) {
      setCsvMessage(err.message);
    }
  };

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  return (
    <div className="dashboard">
      <div className="card">
        <h1>Личный кабинет</h1>
        {user && (
          <>
            <p><strong>Имя:</strong> {user.name}</p>
            <p><strong>Email:</strong> {user.email}</p>
          </>
        )}
        {error && <div className="error">{error}</div>}
      </div>

      {/* <div className="card">
        <h2>Импорт каталога товаров</h2>
        <div className="row">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
          />
          <button className="btn btn-primary" onClick={handleCsvUpload}>
            Загрузить CSV
          </button>
        </div>
        {csvMessage && <p className="muted">{csvMessage}</p>}
      </div> */}

      <div className="card">
        <div className="row between">
          <h2>Получатели подарков</h2>
          <Link to="/recipients/new" className="btn btn-primary">
            Добавить получателя
          </Link>
        </div>

        {recipients.length === 0 ? (
          <p className="muted">Получателей пока нет.</p>
        ) : (
          <div className="recipient-list">
            {recipients.map((recipient) => (
              <div key={recipient.id} className="recipient-item">
                <div>
                  <h3>Получатель #{recipient.id}</h3>
                  <p><strong>Возраст:</strong> {recipient.age}</p>
                  <p><strong>Повод:</strong> {recipient.occasion}</p>
                  <p><strong>Отношения:</strong> {recipient.relationship_type || "—"}</p>
                  <p><strong>Интересы:</strong> {recipient.interests?.join(", ") || "—"}</p>
                  <p><strong>Исключения:</strong> {recipient.exclusions?.join(", ") || "—"}</p>
                </div>

                <div className="actions">
                  <Link
                    to={`/recipients/${recipient.id}/edit`}
                    className="btn btn-secondary"
                  >
                    Редактировать
                  </Link>

                  <Link
                    to={`/recommendations/${recipient.id}`}
                    className="btn btn-primary"
                  >
                    Подобрать подарок
                  </Link>

                  {/* <button
                    className="btn btn-secondary"
                    onClick={async () => {
                      try {
                        const data = await api.getVkAuthUrl(recipient.id);
                        window.location.href = data.auth_url;
                      } catch (err) {
                        alert(err.message);
                      }
                    }}
                  >
                    Импортировать из VK
                  </button> */}

                  <button
                    className="btn btn-secondary"
                    onClick={async () => {
                      const profileInput = window.prompt(
                        "Введите ссылку на VK-профиль или id/username, например:\nhttps://vk.com/id1\nили\nhttps://vk.com/durov"
                      );

                      if (!profileInput) return;

                      try {
                        const result = await api.importVkPublicProfile({
                          recipient_id: recipient.id,
                          profile_input: profileInput
                        });

                        alert(
                          `Импортировано интересов: ${
                            result.imported_interests?.length || 0
                          }\n${(result.imported_interests || []).join(", ")}`
                        );

                        loadData();
                      } catch (err) {
                        alert(err.message);
                      }
                    }}
                  >
                    Импортировать публичные интересы VK
                  </button>

                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(recipient.id)}
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 



