// import { useEffect, useState } from "react";
// import { Link, useParams } from "react-router-dom";
// import { api } from "../api/client";
// import ProductCard from "../components/ProductCard";

// function parseCategories(value) {
//   return value
//     .split(",")
//     .map((item) => item.trim())
//     .filter(Boolean);
// }

// export default function Recommendations() {
//   const { recipientId } = useParams();

//   const [recipient, setRecipient] = useState(null);
//   const [form, setForm] = useState({
//     budget_min: 1000,
//     budget_max: 5000,
//     categories: "",
//     top_k: 10
//   });
//   const [items, setItems] = useState([]);
//   const [loadingRecipient, setLoadingRecipient] = useState(true);
//   const [loadingRecommendations, setLoadingRecommendations] = useState(false);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     const loadRecipient = async () => {
//       try {
//         const data = await api.getRecipient(recipientId);
//         setRecipient(data);
//       } catch (err) {
//         setError(err.message);
//       } finally {
//         setLoadingRecipient(false);
//       }
//     };

//     loadRecipient();
//   }, [recipientId]);

//   const onChange = (e) => {
//     setForm((prev) => ({
//       ...prev,
//       [e.target.name]: e.target.value
//     }));
//   };

//   const onSubmit = async (e) => {
//     e.preventDefault();
//     setError("");
//     setLoadingRecommendations(true);

//     try {
//       const data = await api.generateRecommendations({
//         recipient_id: Number(recipientId),
//         budget_min: Number(form.budget_min),
//         budget_max: Number(form.budget_max),
//         categories: parseCategories(form.categories),
//         top_k: Number(form.top_k)
//       });
//       setItems(data);
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setLoadingRecommendations(false);
//     }
//   };

//   if (loadingRecipient) {
//     return <div className="card">Загрузка...</div>;
//   }

//   return (
//     <div className="recommendations-page">
//       <div className="card">
//         <div className="row between">
//           <h1>Подбор подарка</h1>
//           <Link to="/dashboard" className="btn btn-secondary">
//             Назад
//           </Link>
//         </div>

//         {recipient && (
//           <div className="recipient-summary">
//             <p><strong>Возраст:</strong> {recipient.age}</p>
//             <p><strong>Повод:</strong> {recipient.occasion}</p>
//             <p><strong>Отношения:</strong> {recipient.relationship_type || "—"}</p>
//             <p><strong>Интересы:</strong> {recipient.interests?.join(", ") || "—"}</p>
//             <p><strong>Исключения:</strong> {recipient.exclusions?.join(", ") || "—"}</p>
//           </div>
//         )}
//       </div>

//       <form className="card form-card wide" onSubmit={onSubmit}>
//         <h2>Параметры подбора</h2>

//         <label>Минимальный бюджет</label>
//         <input
//           type="number"
//           name="budget_min"
//           value={form.budget_min}
//           onChange={onChange}
//           min="0"
//           required
//         />

//         <label>Максимальный бюджет</label>
//         <input
//           type="number"
//           name="budget_max"
//           value={form.budget_max}
//           onChange={onChange}
//           min="1"
//           required
//         />

//         <label>Категории (через запятую)</label>
//         <input
//           type="text"
//           name="categories"
//           value={form.categories}
//           onChange={onChange}
//           placeholder="книги, техника"
//         />

//         <label>Количество рекомендаций</label>
//         <input
//           type="number"
//           name="top_k"
//           value={form.top_k}
//           onChange={onChange}
//           min="1"
//           max="20"
//           required
//         />

//         {error && <div className="error">{error}</div>}

//         <button className="btn btn-primary" disabled={loadingRecommendations}>
//           {loadingRecommendations ? "Подбираем..." : "Получить рекомендации"}
//         </button>
//       </form>

//       <div className="recommendations-grid">
//         {items.length === 0 ? (
//           <div className="card">
//             <p className="muted">Рекомендации пока не сгенерированы.</p>
//           </div>
//         ) : (
//           items.map((item) => <ProductCard key={item.product_id} item={item} />)
//         )}
//       </div>
//     </div>
//   );
// }




import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import ProductCard from "../components/ProductCard";

function parseCategories(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function getProductKey(product) {
  return product.product_id ?? product.id;
}

export default function Recommendations() {
  const { recipientId } = useParams();

  const [recipient, setRecipient] = useState(null);
  const [form, setForm] = useState({
    budget_min: 1000,
    budget_max: 5000,
    categories: "",
    top_k: 10
  });

  const [items, setItems] = useState([]);
  const [loadingRecipient, setLoadingRecipient] = useState(true);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [error, setError] = useState("");

  // новые состояния для поиска, фильтрации и избранного
  const [searchQuery, setSearchQuery] = useState("");
  const [resultPriceMin, setResultPriceMin] = useState("");
  const [resultPriceMax, setResultPriceMax] = useState("");
  const [favorites, setFavorites] = useState([]);

  useEffect(() => {
    const loadRecipient = async () => {
      try {
        const data = await api.getRecipient(recipientId);
        setRecipient(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoadingRecipient(false);
      }
    };

    loadRecipient();
  }, [recipientId]);

  const onChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoadingRecommendations(true);

    try {
      const data = await api.generateRecommendations({
        recipient_id: Number(recipientId),
        budget_min: Number(form.budget_min),
        budget_max: Number(form.budget_max),
        categories: parseCategories(form.categories),
        top_k: Number(form.top_k)
      });

      console.log("recommendations response:", data);

      // если backend возвращает массив — оставляем как есть
      // если вдруг вернёт объект {items: []}, тоже обработаем
      if (Array.isArray(data)) {
        setItems(data);
      } else if (Array.isArray(data?.items)) {
        setItems(data.items);
      } else if (Array.isArray(data?.recommendations)) {
        setItems(data.recommendations);
      } else {
        setItems([]);
      }

      // при новой генерации сбрасываем фильтры по результатам и избранное
      setSearchQuery("");
      setResultPriceMin("");
      setResultPriceMax("");
      setFavorites([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const toggleFavorite = (product) => {
    setFavorites((prev) => {
      const exists = prev.some(
        (item) => getProductKey(item) === getProductKey(product)
      );

      if (exists) {
        return prev.filter(
          (item) => getProductKey(item) !== getProductKey(product)
        );
      }

      return [...prev, product];
    });
  };

  const isFavorite = (product) => {
    return favorites.some(
      (item) => getProductKey(item) === getProductKey(product)
    );
  };

  const filteredItems = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    const minPrice =
      resultPriceMin === "" ? null : Number(resultPriceMin);

    const maxPrice =
      resultPriceMax === "" ? null : Number(resultPriceMax);

    return items.filter((item) => {
      const name = item.name?.toLowerCase() || "";
      const category = item.category?.toLowerCase() || "";
      const brand = item.brand?.toLowerCase() || "";
      const description = item.description?.toLowerCase() || "";

      const explanations = Array.isArray(item.explanations)
        ? item.explanations.join(" ").toLowerCase()
        : "";

      const matchesSearch =
        query === "" ||
        name.includes(query) ||
        category.includes(query) ||
        brand.includes(query) ||
        description.includes(query) ||
        explanations.includes(query);

      const price = Number(item.price);

      const matchesMinPrice = minPrice === null || price >= minPrice;
      const matchesMaxPrice = maxPrice === null || price <= maxPrice;

      return matchesSearch && matchesMinPrice && matchesMaxPrice;
    });
  }, [items, searchQuery, resultPriceMin, resultPriceMax]);

  const resetResultFilters = () => {
    setSearchQuery("");
    setResultPriceMin("");
    setResultPriceMax("");
  };

  if (loadingRecipient) {
    return <div className="card">Загрузка...</div>;
  }

  return (
    <div className="recommendations-page">
      <div className="card">
        <div className="row between">
          <h1>Подбор подарка</h1>
          <Link to="/dashboard" className="btn btn-secondary">
            Назад
          </Link>
        </div>

        {recipient && (
          <div className="recipient-summary">
            <p><strong>Возраст:</strong> {recipient.age}</p>
            <p><strong>Пол:</strong> {recipient.gender || "—"}</p>
            <p><strong>Повод:</strong> {recipient.occasion}</p>
            <p><strong>Отношения:</strong> {recipient.relationship_type || "—"}</p>
            <p><strong>Интересы:</strong> {recipient.interests?.join(", ") || "—"}</p>
            <p><strong>Исключения:</strong> {recipient.exclusions?.join(", ") || "—"}</p>
          </div>
        )}
      </div>

      <form className="card form-card wide" onSubmit={onSubmit}>
        <h2>Параметры подбора</h2>

        <label>Минимальный бюджет</label>
        <input
          type="number"
          name="budget_min"
          value={form.budget_min}
          onChange={onChange}
          min="0"
          required
        />

        <label>Максимальный бюджет</label>
        <input
          type="number"
          name="budget_max"
          value={form.budget_max}
          onChange={onChange}
          min="1"
          required
        />

        <label>Категории (через запятую)</label>
        <input
          type="text"
          name="categories"
          value={form.categories}
          onChange={onChange}
          placeholder="книги, техника"
        />

        <label>Количество рекомендаций</label>
        <input
          type="number"
          name="top_k"
          value={form.top_k}
          onChange={onChange}
          min="1"
          max="20"
          required
        />

        {error && <div className="error">{error}</div>}

        <button className="btn btn-primary" disabled={loadingRecommendations}>
          {loadingRecommendations ? "Подбираем..." : "Получить рекомендации"}
        </button>
      </form>

      {/* блок появляется только после генерации рекомендаций */}
      {items.length > 0 && (
        <div className="card form-card wide">
          <h2>Поиск и фильтрация по результатам</h2>

          <label>Поиск по ключевым словам</label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="например: космос, книги, техника"
          />

          <div className="row">
            <div style={{ flex: 1 }}>
              <label>Цена от</label>
              <input
                type="number"
                min="0"
                value={resultPriceMin}
                onChange={(e) => setResultPriceMin(e.target.value)}
                placeholder="0"
              />
            </div>

            <div style={{ flex: 1 }}>
              <label>Цена до</label>
              <input
                type="number"
                min="0"
                value={resultPriceMax}
                onChange={(e) => setResultPriceMax(e.target.value)}
                placeholder="5000"
              />
            </div>
          </div>

          <p className="muted">
            Показано: {filteredItems.length} из {items.length}
          </p>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={resetResultFilters}
          >
            Сбросить фильтры
          </button>
        </div>
      )}

      {/* избранное */}
      {favorites.length > 0 && (
        <div className="card">
          <h2>★ Избранное</h2>

          <div className="recipient-list">
            {favorites.map((item) => (
              <div key={getProductKey(item)} className="recipient-item">
                <div>
                  <strong>{item.name}</strong>
                  <p className="muted">
                    {Number(item.price).toLocaleString("ru-RU")} ₽
                  </p>
                </div>

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => toggleFavorite(item)}
                >
                  Убрать
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="recommendations-grid">
        {items.length === 0 ? (
          <div className="card">
            <p className="muted">Рекомендации пока не сгенерированы.</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="card">
            <p className="muted">
              По текущему поиску и фильтрам ничего не найдено.
            </p>
          </div>
        ) : (
          filteredItems.map((item) => (
            <ProductCard
              key={getProductKey(item)}
              item={item}
              isFavorite={isFavorite(item)}
              onToggleFavorite={toggleFavorite}
            />
          ))
        )}
      </div>
    </div>
  );
}