import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";

function toArray(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function RecipientForm() {
  const { id } = useParams();
  const isEdit = useMemo(() => Boolean(id), [id]);
  const navigate = useNavigate();

  const [form, setForm] = useState({
    age: "",
    gender: "",
    relationship_type: "",
    occasion: "",
    interests: "",
    exclusions: ""
  });

  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEdit) return;

    const loadRecipient = async () => {
      try {
        const data = await api.getRecipient(id);
        setForm({
          age: data.age ?? "",
          gender: data.gender ?? "",
          relationship_type: data.relationship_type ?? "",
          occasion: data.occasion ?? "",
          interests: (data.interests || []).join(", "),
          exclusions: (data.exclusions || []).join(", ")
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadRecipient();
  }, [id, isEdit]);

  const onChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);

    const payload = {
      age: Number(form.age),
      gender: form.gender || null,
      relationship_type: form.relationship_type || null,
      occasion: form.occasion,
      interests: toArray(form.interests),
      exclusions: toArray(form.exclusions)
    };

    try {
      if (isEdit) {
        await api.updateRecipient(id, payload);
      } else {
        await api.createRecipient(payload);
      }
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  return (
    <div className="form-page">
      <form className="card form-card wide" onSubmit={onSubmit}>
        <div className="row between">
          <h1>{isEdit ? "Редактирование получателя" : "Новый получатель"}</h1>
          <Link to="/dashboard" className="btn btn-secondary">
            Назад
          </Link>
        </div>

        <label>Возраст *</label>
        <input
          type="number"
          name="age"
          value={form.age}
          onChange={onChange}
          min="0"
          max="120"
          required
        />
        <label>Пол</label>
        <select
          name="gender"
          value={form.gender}
          onChange={onChange}
        >
          <option value="">Не выбрано</option>
          <option value="мужчина">Мужчина</option>
          <option value="женщина">Женщина</option>
        </select>


        <label>Тип отношений</label>
        <select
          name="relationship_type"
          value={form.relationship_type}
          onChange={onChange}
        >
          <option value="">Не выбрано</option>
          <option value="друг">друг</option>
          <option value="партнёр">партнёр</option>
          <option value="коллега">коллега</option>
          <option value="родственник">родственник</option>
        </select>

        <label>Повод *</label>
        <select
          name="occasion"
          value={form.occasion}
          onChange={onChange}
          required
        >
          <option value="">Выберите повод</option>
          <option value="день рождения">день рождения</option>
          <option value="новый год">новый год</option>
          <option value="юбилей">юбилей</option>
        </select>

        <label>Интересы</label>
        <input
          type="text"
          name="interests"
          value={form.interests}
          onChange={onChange}
          placeholder="космос, книги, техника"
        />

        <label>Исключения («не дарить»)</label>
        <input
          type="text"
          name="exclusions"
          value={form.exclusions}
          onChange={onChange}
          placeholder="дом, еда"
        />

        {error && <div className="error">{error}</div>}

        <button className="btn btn-primary" disabled={saving}>
          {saving ? "Сохраняем..." : "Сохранить"}
        </button>
      </form>
    </div>
  );
}