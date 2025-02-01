import { useState } from 'react'

import Rank from '../components/Rank'

function Leaderboard() {
    const [activeTab, setActiveTab] = useState('1Day')
    const [leaderboardData] = useState([
        { rank: 2, reviews: 600, time: '1Std', streak: '12Tage', retention: '80%' },
        { rank: 3, reviews: 600, time: '1Std', streak: '12Tage', retention: '80%' },
        { rank: 4, reviews: 600, time: '1Std', streak: '12Tage', retention: '80%' },
        { rank: 5, reviews: 600, time: '1Std', streak: '12Tage', retention: '80%' },
    ])

    return (
        <>
        <header>
            <h1>AnkiLeague</h1>
            <nav>
                <span onClick={() => setActiveTab('1Day')}>1 Day</span>
                <span onClick={() => setActiveTab('1Week')}>1 Week</span>
                <span onClick={() => setActiveTab('1Month')}>1 Month</span>
                <span onClick={() => setActiveTab('alltime')}>All</span>
            </nav>
        </header>
        <div className='ranking'>
            <Rank rank={1} name='Max Mustermann' reviews={600} time='1Std' streak='12Tage' retention='80%' />
        </div>
        </>
    )
}

export default Leaderboard