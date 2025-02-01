import { useState, useEffect } from "react";

import api from "../Api"

import Rank from '../components/Rank'

function Leaderboard({route}) {
    const [activeTab, setActiveTab] = useState('day')
    const [leaderboardData, setLeaderboardData] = useState()

    const fetchJuengsteDaten = async () => {
        try {
            const res = await api.post(route, {'period':activeTab, 'sort_by': 'reviews'})
            console.log(res.data)
            setLeaderboardData(res.data)
        } catch (error) {
            console.error('Abrufen der jüngsten Daten ist fehlgeschlagen', error.response ? error.response.data : error.message)
        }
    }

    useEffect(() => {
        fetchJuengsteDaten()

        // Datenabruf alle 5 Sekunden
        const interval = setInterval(() => {
            fetchJuengsteDaten()
        }, 5 * 1000); // 5 Sekunden

        return () => clearInterval(interval);
    }, [activeTab])

    return (
        <>
        <header>
            <h1>AnkiLeague</h1>
            <nav>
                <span className={activeTab === 'day' ? 'selected' : ''} onClick={() => setActiveTab('day')}>1 Day</span>
                <span className={activeTab === 'week' ? 'selected' : ''} onClick={() => setActiveTab('week')}>1 Week</span>
                <span className={activeTab === 'month' ? 'selected' : ''} onClick={() => setActiveTab('month')}>1 Month</span>
                <span className={activeTab === 'alltime' ? 'selected' : ''} onClick={() => setActiveTab('alltime')}>All</span>
            </nav>
        </header>
        <div className='ranking'>
            {leaderboardData && leaderboardData.length > 0 ? (
            // Durch das Array iterieren und für jedes Element ein <Rank>-Component erzeugen
            leaderboardData.map((entry, index) => (
                <Rank
                key={entry.id ?? index}
                // Beispiel: rank = Listenposition (index + 1)
                rank={index + 1}
                // Beispielhafter Zugriff auf Felder in "entry"
                name={entry.name}
                reviews={entry.reviews}
                time={entry.time}
                streak={entry.streak}
                retention={entry.retention}
                />
            ))
            ) : (
            <p>Keine Daten vorhanden.</p>
            )}
        </div>
        </>
    )
}

export default Leaderboard