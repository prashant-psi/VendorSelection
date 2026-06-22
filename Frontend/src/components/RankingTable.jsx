export default function RankingTable({ data }) {
  const rankings = data?.rankings || (Array.isArray(data) ? data : null);

  if (!rankings?.length) {
    return null;
  }

  return (
    <div className="ranking-table-wrap">
      <div className="ranking-meta">
        {data?.scoring_method && (
          <span className="badge">Scoring: {data.scoring_method}</span>
        )}
        {data?.ml_weight != null && data.ml_weight > 0 && (
          <span className="badge">ML blend: {Math.round(data.ml_weight * 100)}%</span>
        )}
      </div>
      <table className="ranking-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Vendor</th>
            <th>Score</th>
            <th>Quality</th>
            <th>Lead time</th>
            <th>Country</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((row) => (
            <tr key={row.vendor_id || row.rank}>
              <td>{row.rank}</td>
              <td>{row.vendor_name}</td>
              <td>{row.final_score ?? "—"}</td>
              <td>{row.overall_quality_score ?? "—"}</td>
              <td>{row.lead_time_days != null ? `${row.lead_time_days}d` : "—"}</td>
              <td>{row.country_code ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
