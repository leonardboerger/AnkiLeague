function Rank({rank, name, reviews, time, streak, retention}){

    return (
        <div className='ranking-item'>
        <h2>{rank}</h2>
        <div className='ranking-item-wrapper'>
            <h3>{name}</h3>
            <div className='wrapper'>
                <div>
                    <p>{reviews}</p>
                    <p>Reviews</p>
                </div>
                <div>
                    <p>{time}</p>
                    <p>Time</p>
                </div>
                <div>
                    <p>{streak}</p>
                    <p>Streak</p>
                </div>
                <div>
                    <p>{retention}</p>
                    <p>Retention</p>
                </div>
            </div>
        </div>
    </div>
    )
}

export default Rank