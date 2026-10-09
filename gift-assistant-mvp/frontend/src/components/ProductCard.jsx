// export default function ProductCard({ item }) {
//   return (
//     <div className="card product-card">
//       <div className="product-card__top">
//         <div>
//           <h3>{item.name}</h3>
//           <p className="muted">{item.category}</p>
//         </div>
//         <div className="price">{item.price} ₽</div>
//       </div>

//       <p>{item.description}</p>

//       {item.brand && <p className="muted">Бренд: {item.brand}</p>}
//       <p className="muted">Score: {item.score}</p>

//       <div className="reasons">
//         <strong>Почему рекомендовано:</strong>
//         <ul>
//           {item.reasons.map((reason, index) => (
//             <li key={index}>{reason}</li>
//           ))}
//         </ul>
//       </div>
//     </div>
//   );
// }




export default function ProductCard({
  item,
  isFavorite = false,
  onToggleFavorite = () => {}
}) {
  return (
    <div className="product-card card">
      <div className="row between">
        <div>
          <h3>{item.name}</h3>
          <p className="muted">{item.category}</p>
        </div>

        <button
          type="button"
          className={isFavorite ? "btn btn-primary" : "btn btn-secondary"}
          onClick={() => onToggleFavorite(item)}
        >
          {isFavorite ? "★ В избранном" : "☆ В избранное"}
        </button>
      </div>

      {item.image_url && (
        <img
          src={item.image_url}
          alt={item.name}
          className="product-image"
        />
      )}

      {item.description && <p>{item.description}</p>}

      <p>
        <strong>Цена:</strong>{" "}
        {Number(item.price).toLocaleString("ru-RU")} ₽
      </p>

      {item.brand && (
        <p>
          <strong>Бренд:</strong> {item.brand}
        </p>
      )}

      {item.explanations?.length > 0 && (
        <div>
          <strong>Почему рекомендуется:</strong>
          <ul>
            {item.explanations.map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {/* score последней строкой */}
      {item.score !== undefined && item.score !== null && (
        <p className="muted product-score">
          Score рекомендации: {Number(item.score).toFixed(4)}
        </p>
      )}
    </div>
  );
}