package cctv.cse.com.cctv_client.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import cctv.cse.com.cctv_client.etc.Item;
import cctv.cse.com.cctv_client.R;

/**
 * Created by sy081 on 2018-09-14.
 * Recycler Popup View Adapter
 */

public class RecyclerPopupWindowAdapter extends RecyclerView.Adapter<RecyclerPopupWindowAdapter.MyViewHolder> {

    private List<Item> items;
    private static final int TYPE_INACTIVE = 0;
    private static final int TYPE_ACTIVE = 1;

    /**
     * This is constructor to set items
     */
    public RecyclerPopupWindowAdapter(List<Item> items) {
        super();
        this.items = items;
    }

    @Override
    public int getItemViewType(int position) {
        Item item = items.get(position);
        return item.isActive() ? TYPE_ACTIVE : TYPE_INACTIVE;
    }

    /**
     * This is function to create view holder
     */
    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        // Set view holder layout.
        int layout = viewType == TYPE_INACTIVE ? R.layout.item_inactive : R.layout.item_active;

        // Return resources defined in xml in a view type using LayoutInflater
        View itemView = LayoutInflater.from(parent.getContext()).inflate(layout, parent, false);
        return new MyViewHolder(itemView, onItemClickListener);
    }

    /**
     * This is function to run recycling view to show
     */
    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Item item = items.get(position);
        holder.getTimeTV().setText(item.getContent());
    }

    /**
     * This is function to return length of item to show
     */
    @Override
    public int getItemCount() {
        return items.size();
    }

    private OnItemClickListener onItemClickListener;

    public void setOnItemClickListener(OnItemClickListener listener) {
        this.onItemClickListener = listener;
    }

    /**
     * This is ViewHolder that holds the view as if the card were in the holder
     */
    class MyViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener {
        private TextView timeTV;
        private OnItemClickListener mListener;

        public MyViewHolder(View rootView, OnItemClickListener listener) {
            super(rootView);
            this.mListener = listener;
            timeTV = rootView.findViewById(R.id.tv_item_time);
            rootView.setOnClickListener(this);
        }

        @Override
        public void onClick(View v) {
            if (mListener != null) {
                mListener.onItemClick(getAdapterPosition());
            }
        }

        public TextView getTimeTV() {
            return timeTV;
        }

    }

    public interface OnItemClickListener {
        void onItemClick(int position);
    }

}